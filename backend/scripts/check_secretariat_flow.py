"""Exercise the academic secretariat (phase 14, delivery 1).

Enrollment movements with their timeline, re-enrollment per term, internal and
external transfers, curriculum change, credit transfers and the transcript
(CR and curriculum completion). Uses a temporary SQLite database by default
(set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_secretariat_check_{os.getpid()}.sqlite3"
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
from app.core.tenancy import bind_institution
from app.models.institution import Institution, InstitutionMembership
from app.models.schedule import ClassEnrollment, ClassEnrollmentResult, ClassEnrollmentStatus
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
    ("admin", UserRole.institution_admin),
    ("coord", UserRole.coordinator),
    ("secretaria", UserRole.secretary),
    ("prof", UserRole.instructor),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
)


def seed() -> tuple[int, dict[str, int]]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="faculdade", name="Faculdade")
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = user.id
        institution_id = institution.id
        db.commit()
    return institution_id, ids


def seed_attempts(institution_id: int, student_id: int, offerings: dict[str, int]) -> None:
    """Cursadas ja concluidas (resultado publicado) nas ofertas de cada disciplina."""
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        for key, grade, result in (("S1", 8, ClassEnrollmentResult.approved), ("OLD", 6, ClassEnrollmentResult.approved),
                                   ("S3", 3, ClassEnrollmentResult.failed)):
            db.add(ClassEnrollment(class_offering_id=offerings[key], student_id=student_id, status=ClassEnrollmentStatus.completed,
                                   final_grade=grade, result=result, enrolled_at=datetime(2027, 2, 1, tzinfo=timezone.utc)))
        db.commit()


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, name: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": f"{name}@example.com", "password": PASSWORD})
        assert response.status_code == 200, f"login {name}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


async def setup_structure(c: Checker, coord: dict) -> dict:
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    await c.call("POST", f"/academic/terms/{term['id']}/status", 200, "open term", coord, json={"status": "open"})
    subjects = {}
    for code, hours, credits in (("S1", 60, 4), ("S2", 60, 4), ("S3", 40, 2), ("OLD", 60, 4), ("E1", 60, 4)):
        subjects[code] = (await c.call("POST", "/academic/subjects", 201, f"subject {code}", coord,
                                       json={"code": code, "name": f"Disciplina {code}", "hours": hours, "credits": credits}))["id"]
    await c.call("POST", f"/academic/subjects/{subjects['OLD']}/equivalences", 201, "OLD equivalent to S2", coord, json={"subject_id": subjects["S2"]})

    programs, curricula = {}, {}
    for code, components in (("ADM", (("S1", 1, "mandatory"), ("S2", 1, "mandatory"), ("S3", 2, "elective"))), ("ECO", (("E1", 1, "mandatory"),))):
        programs[code] = (await c.call("POST", "/academic/programs", 201, f"program {code}", coord,
                                       json={"code": code, "name": f"Programa {code}", "level": "undergraduate", "duration_terms": 8}))["id"]
        curriculum = await c.call("POST", f"/academic/programs/{programs[code]}/curricula", 201, f"curriculum {code}", coord, json={"version": "1"})
        for subject, term_number, kind in components:
            await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, f"component {subject}", coord,
                         json={"subject_id": subjects[subject], "term_number": term_number, "kind": kind})
        await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, f"activate {code}", coord)
        curricula[code] = curriculum["id"]
    v2 = await c.call("POST", f"/academic/curricula/{curricula['ADM']}/versions", 201, "ADM v2", coord, json={"version": "2"})
    await c.call("POST", f"/academic/curricula/{v2['id']}/activate", 200, "activate ADM v2", coord)

    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Curso base"})
    offerings = {}
    for key in ("S1", "OLD", "S3"):
        offerings[key] = (await c.call("POST", "/schedule/classes", 201, f"offering {key}", coord, json={
            "course_id": course["id"], "name": f"Turma {key}", "capacity": 30, "term_id": term["id"], "subject_id": subjects[key],
            "starts_at": "2027-02-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z",
        }))["id"]
    return {"term": term["id"], "subjects": subjects, "programs": programs, "curricula": curricula, "adm_v2": v2["id"], "offerings": offerings}


async def check_movements(c: Checker, h: dict, ids: dict, ctx: dict) -> dict[str, int]:
    sec = h["secretaria"]
    ana = await c.call("POST", "/academic/program-enrollments", 201, "secretary enrolls ana", sec,
                       json={"student_id": ids["ana"], "program_id": ctx["programs"]["ADM"], "curriculum_id": ctx["curricula"]["ADM"]})
    base = f"/secretariat/enrollments/{ana['id']}"
    await c.call("POST", f"{base}/registrations", 201, "reenroll term", sec, json={"term_id": ctx["term"], "curriculum_term_number": 1})
    await c.call("POST", f"{base}/registrations", 409, "reenroll twice", sec, json={"term_id": ctx["term"]})
    await c.call("POST", f"{base}/registrations", 400, "term number beyond duration", sec, json={"term_id": ctx["term"], "curriculum_term_number": 9})
    regs = await c.call("GET", f"{base}/registrations", 200, "list registrations", sec)
    c.expect([(r["term_name"], r["curriculum_term_number"]) for r in regs] == [("2027", 1)], f"registrations: {regs}")

    locked = await c.call("POST", f"{base}/lock", 200, "lock", sec, json={"reason": "Viagem"})
    c.expect(locked.get("status") == "locked", f"locked: {locked}")
    await c.call("POST", f"{base}/lock", 409, "lock twice", sec, json={})
    await c.call("POST", f"{base}/reactivate", 200, "reactivate", sec, json={"reason": "Retorno"})
    await c.call("POST", f"{base}/change-curriculum", 200, "migrate to v2", sec, json={"curriculum_id": ctx["adm_v2"], "reason": "Nova matriz"})
    await c.call("POST", f"{base}/change-curriculum", 409, "already on v2", sec, json={"curriculum_id": ctx["adm_v2"]})
    await c.call("POST", f"{base}/change-curriculum", 404, "curriculum of another program", sec, json={"curriculum_id": ctx["curricula"]["ECO"]})
    await c.call("POST", f"{base}/lock", 403, "instructor blocked", h["prof"], json={})
    await c.call("GET", base, 403, "student blocked", h["ana"])

    bia = await c.call("POST", "/academic/program-enrollments", 201, "enroll bia", sec, json={"student_id": ids["bia"], "program_id": ctx["programs"]["ADM"]})
    await c.call("POST", f"/secretariat/enrollments/{bia['id']}/transfer-internal", 400, "same program", sec, json={"program_id": ctx["programs"]["ADM"]})
    moved = await c.call("POST", f"/secretariat/enrollments/{bia['id']}/transfer-internal", 201, "internal transfer", sec,
                         json={"program_id": ctx["programs"]["ECO"], "reason": "Mudança de curso"})
    c.expect(moved.get("program", {}).get("code") == "ECO" and moved.get("status") == "active", f"new enrollment in ECO: {moved}")
    old = await c.call("GET", f"/secretariat/enrollments/{bia['id']}", 200, "old enrollment", sec)
    c.expect(old.get("status") == "transferred", f"old enrollment transferred: {old.get('status')}")
    new_events = await c.call("GET", f"/secretariat/enrollments/{moved['id']}/events", 200, "new enrollment events", sec)
    c.expect([e["kind"] for e in new_events] == ["enrolled", "transferred_internal"], f"new enrollment timeline: {new_events}")

    await c.call("POST", f"/academic/program-enrollments/{moved['id']}/status", 200, "status via academic route", h["coord"], json={"status": "locked"})
    moved_events = await c.call("GET", f"/secretariat/enrollments/{moved['id']}/events", 200, "events after direct change", sec)
    c.expect(moved_events[-1]["kind"] == "locked", f"direct status change is recorded: {moved_events[-1]}")
    return {"ana": ana["id"], "bia_old": bia["id"]}


async def check_credits_and_transcript(c: Checker, h: dict, ctx: dict, enrollment_id: int) -> None:
    sec, coord = h["secretaria"], h["coord"]
    credits = f"/secretariat/enrollments/{enrollment_id}/credit-transfers"
    await c.call("POST", credits, 400, "subject outside curriculum", sec, json={"subject_id": ctx["subjects"]["E1"], "source_subject": "X"})
    transfer = await c.call("POST", credits, 201, "request credit", sec, json={
        "subject_id": ctx["subjects"]["S3"], "source_institution": "Faculdade X", "source_subject": "Tópicos", "grade": 9, "hours": 40,
    })
    await c.call("POST", credits, 409, "duplicate credit", sec, json={"subject_id": ctx["subjects"]["S3"], "source_subject": "Y"})
    decision = f"/secretariat/credit-transfers/{transfer['id']}/decision"
    await c.call("POST", decision, 403, "secretary cannot decide", sec, json={"approved": True})

    before = await c.call("GET", f"/secretariat/enrollments/{enrollment_id}/transcript", 200, "transcript before", sec)
    status = {row["code"]: row["status"] for row in before["rows"]}
    c.expect(status == {"S1": "completed", "S2": "completed", "S3": "failed"}, f"transcript statuses (S2 via equivalence): {status}")

    await c.call("POST", decision, 200, "coordination approves", coord, json={"approved": True, "note": "Ementa compatível"})
    await c.call("POST", decision, 409, "already decided", coord, json={"approved": False})

    transcript = await c.call("GET", f"/secretariat/enrollments/{enrollment_id}/transcript", 200, "transcript", sec)
    rows = {row["code"]: (row["status"], row["grade"], row["taken_in"]) for row in transcript["rows"]}
    c.expect(rows == {"S1": ("completed", 8.0, "2027"), "S2": ("completed", 6.0, "2027"), "S3": ("credited", 9.0, "Faculdade X")}, f"transcript rows: {rows}")
    summary = transcript["summary"]
    expected = {"cr": 7.4, "mandatory_hours": 120, "mandatory_hours_done": 120, "elective_hours_done": 40, "hours_done": 160,
                "integralization": 100.0, "completed_components": 3, "total_components": 3}
    c.expect(summary == expected, f"transcript summary: {summary}")
    mine = await c.call("GET", "/secretariat/my/transcripts", 200, "student transcripts", h["ana"])
    c.expect([t["program_code"] for t in mine] == ["ADM"] and mine[0]["summary"]["cr"] == 7.4, f"student sees own transcript: {mine}")

    base = f"/secretariat/enrollments/{enrollment_id}"
    await c.call("POST", f"{base}/transfer-out", 200, "external transfer", sec, json={"destination": "Universidade Y", "reason": "Mudança de cidade"})
    await c.call("POST", f"{base}/lock", 409, "transferred is final", sec, json={})
    await c.call("POST", credits, 409, "closed enrollment gets no credit", sec, json={"subject_id": ctx["subjects"]["S1"], "source_subject": "Z"})
    events = await c.call("GET", f"{base}/events", 200, "timeline", sec)
    c.expect([e["kind"] for e in events] == ["enrolled", "reenrolled", "locked", "reactivated", "curriculum_changed", "transferred_out"],
             f"timeline kinds: {[e['kind'] for e in events]}")
    c.expect(events[-1]["details"] == {"destination": "Universidade Y"} and events[2]["reason"] == "Viagem", f"event details: {events}")


async def run() -> int:
    institution_id, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(name) for name, _ in USERS}
        ctx = await setup_structure(c, h["coord"])
        seed_attempts(institution_id, ids["ana"], ctx["offerings"])
        enrollments = await check_movements(c, h, ids, ctx)
        await check_credits_and_transcript(c, h, ctx, enrollments["ana"])

    if c.failures:
        print("Secretariat flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Secretariat flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
