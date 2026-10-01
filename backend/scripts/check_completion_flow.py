"""Exercise completion requirements (phase 16, delivery 2): credits and integralization, complementary activities,
supervised internship hours, final project (TCC), advising view and the conclusion check.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_completion_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import anyio.to_thread
import fastapi.routing
import httpx
import starlette.concurrency
import starlette.routing

import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.institution import Institution, InstitutionMembership, InstitutionType
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.schedule import ClassEnrollment, ClassEnrollmentResult
from app.models.student import Student, UserRole
from main import app


async def run_in_threadpool_inline(func, *args, **kwargs):
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("cancellable", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)


fastapi.routing.run_in_threadpool = run_in_threadpool_inline
starlette.concurrency.run_in_threadpool = run_in_threadpool_inline
starlette.routing.run_in_threadpool = run_in_threadpool_inline
anyio.to_thread.run_sync = run_in_threadpool_inline

PASSWORD = "secret123"
USERS = (
    ("coord", UserRole.coordinator),
    ("secretaria", UserRole.secretary),
    ("prof", UserRole.instructor),
    ("outro", UserRole.instructor),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
)


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="faculdade", name="Faculdade", type=InstitutionType.university)
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = user.id
        db.commit()
    return ids


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, email: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


def requirement(report: dict, key: str) -> tuple[int, int, bool]:
    item = next(item for item in report["requirements"] if item["key"] == key)
    return item["done"], item["required"], item["met"]


async def setup_structure(c: Checker, h: dict, ids: dict) -> dict:
    """Direito: S1 e S2 (4 creditos, 60h cada); 20h de atividades, 10h de estagio, TCC e 8 creditos."""
    coord = h["coord"]
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027.1", "starts_on": "2027-02-01", "ends_on": "2027-06-30"})
    program = await c.call("POST", "/academic/programs", 201, "program", coord, json={
        "code": "DIR", "name": "Direito", "level": "undergraduate", "total_credits": 8,
        "complementary_hours": 20, "internship_hours": 10, "requires_final_project": True,
    })
    c.expect(program.get("requires_final_project") is True and program.get("internship_hours") == 10, f"program targets: {program}")
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Direito EAD"})
    offerings = []
    for code in ("S1", "S2"):
        subject = await c.call("POST", "/academic/subjects", 201, f"subject {code}", coord, json={"code": code, "name": code, "hours": 60, "credits": 4})
        await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, f"component {code}", coord,
                     json={"subject_id": subject["id"], "term_number": 1})
        offering = await c.call("POST", "/schedule/classes", 201, f"offering {code}", coord, json={
            "course_id": course["id"], "name": f"{code}-A", "capacity": 10, "status": "open", "term_id": term["id"],
            "subject_id": subject["id"], "starts_at": "2027-02-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z",
        })
        offerings.append(offering["id"])
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    enrollments = {}
    for name in ("ana", "bia"):
        enrollments[name] = (await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                          json={"student_id": ids[name], "program_id": program["id"]}))["id"]
    return {"enrollments": enrollments, "offerings": offerings}


async def check_initial_and_credits(c: Checker, h: dict, ctx: dict) -> None:
    sec, ana = h["secretaria"], ctx["enrollments"]["ana"]
    report = await c.call("GET", f"/completion/enrollments/{ana}/integralization", 200, "initial integralization", sec)
    keys = [item["key"] for item in report["requirements"]]
    c.expect(keys == ["mandatory_hours", "credits", "complementary_hours", "internship_hours", "final_project"], f"requirements: {keys}")
    c.expect(report["complete"] is False and requirement(report, "credits") == (0, 8, False), f"initial: {report}")
    await c.call("GET", f"/completion/enrollments/{ana}/integralization", 403, "student uses own view", h["ana"])
    for offering_id in ctx["offerings"]:
        await c.call("POST", f"/registration/program-enrollments/{ana}/offerings/{offering_id}", 200, "office registers", sec, json={})
    with SessionLocal() as db:
        for enrollment in db.query(ClassEnrollment).filter(ClassEnrollment.class_offering_id.in_(ctx["offerings"])).all():
            enrollment.result, enrollment.final_grade = ClassEnrollmentResult.approved, 8.0
        db.commit()
    mine = await c.call("GET", "/completion/my/integralization", 200, "student integralization", h["ana"])
    c.expect(len(mine) == 1 and requirement(mine[0], "credits") == (8, 8, True), f"credits done: {mine}")
    c.expect(requirement(mine[0], "mandatory_hours") == (120, 120, True), f"mandatory hours: {mine}")
    check = await c.call("GET", f"/secretariat/enrollments/{ana}/conclusion", 200, "conclusion check", sec)
    c.expect(check["eligible"] is False and "TCC ainda não aprovado" in check["missing"]
             and "Atividades complementares: 0h de 20h" in check["missing"], f"missing: {check}")


async def check_activities(c: Checker, h: dict, ctx: dict, ids: dict) -> None:
    sec, ana_headers, ana = h["secretaria"], h["ana"], ctx["enrollments"]["ana"]
    path = f"/completion/my/enrollments/{ana}/activities"
    first = await c.call("POST", path, 201, "submit monitoring", ana_headers,
                         json={"category": "teaching", "title": "Monitoria", "occurred_on": "2027-03-01", "hours_requested": 15})
    second = await c.call("POST", path, 201, "submit event", ana_headers,
                          json={"category": "cultural", "title": "Semana jurídica", "occurred_on": "2027-04-01", "hours_requested": 10})
    temp = await c.call("POST", path, 201, "submit to withdraw", ana_headers,
                        json={"title": "Engano", "occurred_on": "2027-04-01", "hours_requested": 2})
    await c.call("POST", path, 404, "bia cannot submit to ana's enrollment", h["bia"], json={"title": "X", "occurred_on": "2027-04-01", "hours_requested": 2})
    await c.call("DELETE", f"/completion/my/activities/{temp['id']}", 404, "bia cannot withdraw", h["bia"])
    await c.call("DELETE", f"/completion/my/activities/{temp['id']}", 204, "ana withdraws", ana_headers)
    decision = f"/completion/activities/{first['id']}/decision"
    await c.call("POST", decision, 403, "instructor cannot decide", h["prof"], json={"approved": True})
    await c.call("POST", decision, 400, "more hours than requested", sec, json={"approved": True, "hours_approved": 20})
    approved = await c.call("POST", decision, 200, "approve partially", sec, json={"approved": True, "hours_approved": 12, "note": "Limite da categoria"})
    c.expect(approved["status"] == "approved" and approved["hours_approved"] == 12, f"approved: {approved}")
    await c.call("POST", decision, 409, "decide twice", sec, json={"approved": False})
    await c.call("DELETE", f"/completion/my/activities/{first['id']}", 409, "cannot withdraw decided", ana_headers)
    rejected = await c.call("POST", f"/completion/activities/{second['id']}/decision", 200, "reject", sec, json={"approved": False})
    c.expect(rejected["hours_approved"] is None, f"rejected: {rejected}")
    third = await c.call("POST", path, 201, "submit research", ana_headers,
                         json={"category": "research", "title": "Iniciação científica", "occurred_on": "2027-05-01", "hours_requested": 8})
    await c.call("POST", f"/completion/activities/{third['id']}/decision", 200, "approve research", sec, json={"approved": True})
    listed = await c.call("GET", f"/completion/enrollments/{ana}/activities", 200, "office list", sec)
    c.expect(len(listed) == 3, f"activities: {listed}")
    report = await c.call("GET", f"/completion/enrollments/{ana}/integralization", 200, "after activities", sec)
    c.expect(requirement(report, "complementary_hours") == (20, 20, True), f"complementary: {report}")
    with SessionLocal() as db:
        notices = db.query(NotificationEvent).filter(
            NotificationEvent.event_type == NotificationEventType.activity_reviewed, NotificationEvent.recipient_student_id == ids["ana"]
        ).count()
    c.expect(notices == 3, f"student notified of each decision: {notices}")


async def check_internship(c: Checker, h: dict, ctx: dict, ids: dict) -> None:
    sec, ana_headers, ana = h["secretaria"], h["ana"], ctx["enrollments"]["ana"]
    base = f"/completion/enrollments/{ana}/internships"
    payload = {"company_name": "Escritório Silva", "supervisor_name": "Dra. Silva", "advisor_id": ids["prof"],
               "starts_on": "2027-03-01", "ends_on": "2027-06-30", "planned_hours": 10}
    await c.call("POST", base, 400, "advisor must be teaching staff", sec, json={**payload, "advisor_id": ids["bia"]})
    await c.call("POST", base, 403, "student cannot register internship", ana_headers, json=payload)
    internship = await c.call("POST", base, 201, "register internship", sec, json=payload)
    optional = await c.call("POST", base, 201, "non-mandatory internship", sec, json={**payload, "is_mandatory": False, "company_name": "ONG"})
    logs = f"/completion/my/internships/{internship['id']}/logs"
    first = await c.call("POST", logs, 201, "log hours", ana_headers, json={"worked_on": "2027-03-02", "hours": 6, "activities": "Pesquisa de jurisprudência"})
    second = await c.call("POST", logs, 201, "log more hours", ana_headers, json={"worked_on": "2027-03-03", "hours": 6, "activities": "Audiência"})
    extra = await c.call("POST", f"/completion/my/internships/{optional['id']}/logs", 201, "optional hours", ana_headers,
                         json={"worked_on": "2027-03-04", "hours": 8, "activities": "Atendimento"})
    await c.call("POST", logs, 400, "date outside the internship", ana_headers, json={"worked_on": "2027-08-01", "hours": 2, "activities": "X"})
    await c.call("POST", logs, 404, "bia cannot log on ana's internship", h["bia"], json={"worked_on": "2027-03-05", "hours": 2, "activities": "X"})
    await c.call("GET", f"/completion/internships/{internship['id']}/logs", 404, "bia cannot read logs", h["bia"])
    await c.call("GET", f"/completion/internships/{internship['id']}/logs", 404, "other instructor cannot read", h["outro"])
    listed = await c.call("GET", f"/completion/internships/{internship['id']}/logs", 200, "advisor reads logs", h["prof"])
    c.expect(len(listed) == 2, f"logs: {listed}")
    await c.call("POST", f"/completion/internship-logs/{first['id']}/review", 403, "other instructor cannot review", h["outro"], json={"approved": True})
    await c.call("POST", f"/completion/internship-logs/{first['id']}/review", 403, "secretary does not supervise", sec, json={"approved": True})
    await c.call("POST", f"/completion/internship-logs/{first['id']}/review", 200, "advisor approves", h["prof"], json={"approved": True})
    await c.call("DELETE", f"/completion/my/internship-logs/{first['id']}", 409, "cannot remove validated log", ana_headers)
    await c.call("POST", f"/completion/internship-logs/{second['id']}/review", 200, "coordination approves", h["coord"], json={"approved": True})
    await c.call("POST", f"/completion/internship-logs/{extra['id']}/review", 200, "coordination approves optional", h["coord"], json={"approved": True})
    mine = await c.call("GET", "/completion/my/internships", 200, "student internships", ana_headers)
    hours = {item["company_name"]: item["approved_hours"] for item in mine}
    c.expect(hours == {"Escritório Silva": 12, "ONG": 8}, f"approved hours per internship: {hours}")
    report = await c.call("GET", f"/completion/enrollments/{ana}/integralization", 200, "after internship", sec)
    c.expect(requirement(report, "internship_hours") == (12, 10, True), f"only mandatory internship counts: {report}")
    advising = await c.call("GET", "/completion/advising", 200, "advisor view", h["prof"])
    c.expect([i["id"] for i in advising["internships"]] == [internship["id"], optional["id"]], f"advising: {advising}")
    empty = await c.call("GET", "/completion/advising", 200, "other advisor view", h["outro"])
    c.expect(empty["internships"] == [] and empty["final_projects"] == [], f"nothing advised: {empty}")
    await c.call("GET", "/completion/advising", 403, "student has no advising", ana_headers)
    advisors = await c.call("GET", "/completion/advisors", 200, "secretary lists advisors", sec)
    c.expect([a["name"] for a in advisors] == ["Coord", "Outro", "Prof"], f"advisors: {advisors}")
    closed = await c.call("PATCH", f"/completion/internships/{internship['id']}", 200, "complete internship", sec, json={"status": "completed"})
    c.expect(closed["status"] == "completed", f"completed: {closed}")
    await c.call("POST", logs, 409, "no logs after completion", ana_headers, json={"worked_on": "2027-03-10", "hours": 2, "activities": "X"})


async def check_final_project(c: Checker, h: dict, ctx: dict, ids: dict) -> None:
    sec, ana = h["secretaria"], ctx["enrollments"]["ana"]
    path = f"/completion/enrollments/{ana}/final-project"
    none = await c.call("GET", path, 200, "no project yet", sec)
    c.expect(none is None or none == {}, f"no project: {none}")
    project = await c.call("PUT", path, 200, "register project", sec, json={"title": "Responsabilidade civil digital", "advisor_id": ids["prof"]})
    result = f"/completion/final-projects/{project['id']}/result"
    await c.call("POST", result, 403, "other instructor", h["outro"], json={"status": "submitted"})
    submitted = await c.call("POST", result, 200, "advisor registers delivery", h["prof"], json={"status": "submitted"})
    c.expect(submitted["status"] == "submitted", f"submitted: {submitted}")
    advising = await c.call("GET", "/completion/advising", 200, "advisor sees project", h["prof"])
    c.expect([p["id"] for p in advising["final_projects"]] == [project["id"]], f"advised projects: {advising}")
    await c.call("POST", result, 400, "defense date required", h["prof"], json={"status": "approved"})
    approved = await c.call("POST", result, 200, "approved at defense", h["prof"],
                            json={"status": "approved", "defense_on": "2027-06-20", "grade": 9.5, "committee": "Prof. A, Prof. B"})
    c.expect(approved["status"] == "approved" and approved["grade"] == 9.5, f"approved: {approved}")
    await c.call("POST", result, 409, "already graded", h["prof"], json={"status": "failed", "defense_on": "2027-06-21"})
    await c.call("PUT", path, 409, "approved project is final", sec, json={"title": "Outro"})
    mine = await c.call("GET", "/completion/my/final-projects", 200, "student projects", h["ana"])
    c.expect([p["status"] for p in mine] == ["approved"], f"student sees project: {mine}")

    bia = ctx["enrollments"]["bia"]
    failed_project = await c.call("PUT", f"/completion/enrollments/{bia}/final-project", 200, "bia project", sec, json={"title": "Tema"})
    await c.call("POST", f"/completion/final-projects/{failed_project['id']}/result", 200, "coordination fails it", h["coord"],
                 json={"status": "failed", "defense_on": "2027-06-20", "grade": 3})
    retry = await c.call("PUT", f"/completion/enrollments/{bia}/final-project", 200, "new attempt", sec, json={"title": "Novo tema"})
    c.expect(retry["status"] == "in_progress" and retry["grade"] is None, f"new attempt resets: {retry}")


async def check_conclusion(c: Checker, h: dict, ctx: dict) -> None:
    sec, ana = h["secretaria"], ctx["enrollments"]["ana"]
    report = await c.call("GET", f"/completion/enrollments/{ana}/integralization", 200, "final integralization", sec)
    c.expect(report["complete"] is True, f"all requirements met: {report}")
    check = await c.call("GET", f"/secretariat/enrollments/{ana}/conclusion", 200, "conclusion check", sec)
    c.expect(check["eligible"] is True and check["missing"] == [], f"eligible: {check}")
    await c.call("POST", f"/secretariat/enrollments/{ana}/conclusion", 200, "conclude", sec, json={"concluded_on": "2027-07-01"})
    await c.call("POST", f"/completion/my/enrollments/{ana}/activities", 409, "graduated enrollment is closed", h["ana"],
                 json={"title": "Tarde", "occurred_on": "2027-07-02", "hours_requested": 2})


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        await check_initial_and_credits(c, h, ctx)
        await check_activities(c, h, ctx, ids)
        await check_internship(c, h, ctx, ids)
        await check_final_project(c, h, ctx, ids)
        await check_conclusion(c, h, ctx)

    if c.failures:
        print("Completion flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Completion flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
