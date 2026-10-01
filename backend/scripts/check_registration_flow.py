"""Exercise subject registration (phase 16, delivery 1): windows, weekly slots, prerequisites, schedule clashes,
credit limit, seats with waitlist promotion and secretariat overrides.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_registration_check_{os.getpid()}.sqlite3"
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

from scripts.check_support import ApiClient  # noqa: E402
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
    ("ana", UserRole.student),
    ("bia", UserRole.student),
    ("carla", UserRole.student),
    ("davi", UserRole.student),
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
            ids[name] = str(user.id)
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


def iso(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


async def setup_structure(c: Checker, h: dict, ids: dict) -> dict:
    """Direito: INTRO (4cr) -> AVANC (4cr, exige INTRO), ETICA (2cr), ELET (optativa, 2cr); ofertas no periodo 2027.1."""
    coord = h["coord"]
    old_term = await c.call("POST", "/academic/terms", 201, "old term", coord, json={"name": "2026.2", "starts_on": "2026-08-01", "ends_on": "2026-12-15"})
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027.1", "starts_on": "2027-02-01", "ends_on": "2027-06-30"})
    other_term = await c.call("POST", "/academic/terms", 201, "other term", coord, json={"name": "2027.2", "starts_on": "2027-08-01", "ends_on": "2027-12-15"})
    program = await c.call("POST", "/academic/programs", 201, "program", coord, json={"code": "DIR", "name": "Direito", "level": "undergraduate"})
    subjects = {}
    for code, credits in (("INTRO", 4), ("AVANC", 4), ("ETICA", 2), ("ELET", 2)):
        subjects[code] = (await c.call("POST", "/academic/subjects", 201, f"subject {code}", coord,
                                       json={"code": code, "name": code.title(), "hours": credits * 15, "credits": credits}))["id"]
    await c.call("POST", f"/academic/subjects/{subjects['AVANC']}/prerequisites", 201, "prerequisite", coord,
                 json={"subject_id": subjects["INTRO"]})
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
    for code, term_number, kind in (("INTRO", 1, "mandatory"), ("ETICA", 1, "mandatory"), ("AVANC", 2, "mandatory"), ("ELET", 2, "elective")):
        await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, f"component {code}", coord,
                     json={"subject_id": subjects[code], "term_number": term_number, "kind": kind})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    enrollments = {}
    for name in ("ana", "bia", "carla"):
        enrollments[name] = (await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                          json={"student_id": ids[name], "program_id": program["id"]}))["id"]
    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Direito EAD"})

    async def offering(name: str, subject: str, capacity: int, term_id: int = term["id"]) -> int:
        created = await c.call("POST", "/schedule/classes", 201, f"offering {name}", coord, json={
            "course_id": course["id"], "name": name, "capacity": capacity, "status": "open", "instructor_id": ids["prof"],
            "starts_at": "2027-02-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z", "term_id": term_id, "subject_id": subjects[subject],
        })
        return created["id"]

    offerings = {
        "INTRO-A": await offering("INTRO-A", "INTRO", 1),
        "ETICA-A": await offering("ETICA-A", "ETICA", 10),
        "ETICA-B": await offering("ETICA-B", "ETICA", 10),
        "AVANC-A": await offering("AVANC-A", "AVANC", 10),
        "ELET-A": await offering("ELET-A", "ELET", 10),
        "INTRO-OLD": await offering("INTRO-OLD", "INTRO", 10, old_term["id"]),
        "INTRO-NEXT": await offering("INTRO-NEXT", "INTRO", 10, other_term["id"]),
    }
    return {"term": term["id"], "program": program["id"], "subjects": subjects, "enrollments": enrollments, "offerings": offerings}


async def check_setup_permissions(c: Checker, h: dict, ctx: dict) -> int:
    sec, off = h["secretaria"], ctx["offerings"]
    window = {"term_id": ctx["term"], "program_id": ctx["program"], "name": "Matrícula 2027.1",
              "opens_at": iso(-timedelta(hours=1)), "closes_at": iso(timedelta(days=2)), "min_credits": 4, "max_credits": 7}
    await c.call("POST", "/registration/windows", 403, "student cannot open window", h["ana"], json=window)
    await c.call("POST", "/registration/windows", 400, "closes before opening", sec, json={**window, "closes_at": iso(-timedelta(days=1))})
    await c.call("POST", "/registration/windows", 400, "min above max", sec, json={**window, "min_credits": 10})
    created = await c.call("POST", "/registration/windows", 201, "secretary opens window", sec, json=window)
    c.expect(created.get("is_open") is True and created.get("program_name") == "Direito", f"window: {created}")

    slots = {"INTRO-A": (0, "08:00", "10:00"), "ETICA-A": (0, "09:00", "11:00"), "ETICA-B": (3, "08:00", "10:00"),
             "AVANC-A": (1, "08:00", "10:00"), "ELET-A": (2, "08:00", "10:00")}
    for name, (weekday, start, end) in slots.items():
        await c.call("POST", f"/registration/offerings/{off[name]}/time-slots", 201, f"slot {name}", h["coord"],
                     json={"weekday": weekday, "starts_at": start, "ends_at": end})
    await c.call("POST", f"/registration/offerings/{off['INTRO-A']}/time-slots", 409, "overlapping slot", h["coord"],
                 json={"weekday": 0, "starts_at": "09:30", "ends_at": "10:30"})
    await c.call("POST", f"/registration/offerings/{off['INTRO-A']}/time-slots", 403, "instructor cannot set slots", h["prof"],
                 json={"weekday": 4, "starts_at": "08:00", "ends_at": "10:00"})
    await c.call("POST", f"/registration/offerings/{off['INTRO-A']}/time-slots", 422, "end before start", h["coord"],
                 json={"weekday": 4, "starts_at": "10:00", "ends_at": "08:00"})
    await c.call("POST", f"/schedule/classes/{off['INTRO-A']}/join", 400, "generic join refuses subject offering", h["ana"])
    return created["id"]


def situation(catalog: dict, name: str) -> dict:
    return next(item for item in catalog["offerings"] if item["offering_name"] == name)


async def check_student_registration(c: Checker, h: dict, ctx: dict, window_id: int) -> None:
    ana, bia, off = h["ana"], h["bia"], ctx["offerings"]
    base = f"/registration/my/windows/{window_id}"
    mine = await c.call("GET", "/registration/my/windows", 200, "open windows", ana)
    c.expect([w["window"]["id"] for w in mine] == [window_id], f"open windows: {mine}")
    none = await c.call("GET", "/registration/my/windows", 200, "no program, no window", h["davi"])
    c.expect(none == [], f"student without enrollment: {none}")
    await c.call("GET", f"{base}/catalog", 404, "catalog without enrollment", h["davi"])

    catalog = await c.call("GET", f"{base}/catalog", 200, "catalog", ana)
    c.expect(situation(catalog, "INTRO-A")["situation"] == "available", f"INTRO available: {catalog}")
    avanc = situation(catalog, "AVANC-A")
    c.expect(avanc["situation"] == "blocked" and "Pré-requisito pendente: Intro" in avanc["blockers"], f"AVANC blocked: {avanc}")
    c.expect("INTRO-OLD" not in [i["offering_name"] for i in catalog["offerings"]], "only offerings of the window term")

    result = await c.call("POST", f"{base}/offerings/{off['INTRO-A']}", 200, "ana takes INTRO", ana)
    c.expect(result.get("result") == "enrolled", f"enrolled: {result}")
    await c.call("POST", f"{base}/offerings/{off['INTRO-A']}", 409, "twice", ana)
    clash = await c.call("POST", f"{base}/offerings/{off['ETICA-A']}", 409, "schedule clash", ana)
    c.expect("Choque de horário com INTRO-A" in clash.get("detail", ""), f"clash detail: {clash}")
    await c.call("POST", f"{base}/offerings/{off['AVANC-A']}", 409, "missing prerequisite", ana)
    await c.call("POST", f"{base}/offerings/{off['ETICA-B']}", 200, "ana takes ETICA-B", ana)
    same = await c.call("GET", f"{base}/catalog", 200, "catalog after", ana)
    c.expect(situation(same, "ETICA-A")["situation"] == "blocked", "same subject blocked")
    c.expect(same["credits_registered"] == 6, f"credits: {same['credits_registered']}")
    over = await c.call("POST", f"{base}/offerings/{off['ELET-A']}", 409, "credit limit", ana)
    c.expect("limite de 7 créditos" in over.get("detail", ""), f"limit detail: {over}")
    await c.call("POST", f"{base}/offerings/{off['INTRO-NEXT']}", 400, "offering of another term", ana)

    waiting = await c.call("POST", f"{base}/offerings/{off['INTRO-A']}", 200, "bia waits for INTRO", bia)
    c.expect(waiting.get("result") == "waitlisted" and waiting.get("waitlist_position") == 1, f"waitlisted: {waiting}")
    catalog_bia = await c.call("GET", f"{base}/catalog", 200, "bia catalog", bia)
    c.expect(situation(catalog_bia, "INTRO-A")["situation"] == "waitlisted", f"bia waitlisted: {catalog_bia}")

    await c.call("DELETE", f"{base}/offerings/{off['INTRO-A']}", 204, "ana drops INTRO", ana)
    catalog_bia = await c.call("GET", f"{base}/catalog", 200, "bia catalog after promotion", bia)
    c.expect(situation(catalog_bia, "INTRO-A")["situation"] == "enrolled", f"bia promoted: {catalog_bia}")
    with SessionLocal() as db:
        promoted = db.query(NotificationEvent).filter(
            NotificationEvent.event_type == NotificationEventType.waitlist_promoted, NotificationEvent.recipient_student_id == ctx["ids"]["bia"]
        ).count()
    c.expect(promoted == 1, f"bia notified: {promoted}")
    await c.call("DELETE", f"{base}/offerings/{off['INTRO-A']}", 404, "ana no longer enrolled", ana)
    again = await c.call("POST", f"{base}/offerings/{off['INTRO-A']}", 200, "ana back to waitlist", ana)
    c.expect(again.get("result") == "waitlisted", f"ana waits now: {again}")
    await c.call("DELETE", f"{base}/offerings/{off['INTRO-A']}", 204, "ana leaves the waitlist", ana)


async def check_prior_approval(c: Checker, h: dict, ctx: dict, window_id: int) -> None:
    """Carla foi aprovada em INTRO no periodo anterior: AVANC liberada, INTRO bloqueada."""
    off, sec = ctx["offerings"], h["secretaria"]
    await c.call("POST", f"/registration/program-enrollments/{ctx['enrollments']['carla']}/offerings/{off['INTRO-OLD']}", 200,
                 "office enrolls carla in old INTRO", sec, json={})
    with SessionLocal() as db:
        enrollment = db.query(ClassEnrollment).filter(ClassEnrollment.class_offering_id == off["INTRO-OLD"]).one()
        enrollment.result, enrollment.final_grade = ClassEnrollmentResult.approved, 8.0
        db.commit()
    base = f"/registration/my/windows/{window_id}"
    catalog = await c.call("GET", f"{base}/catalog", 200, "carla catalog", h["carla"])
    c.expect(situation(catalog, "AVANC-A")["situation"] == "available", f"AVANC open to carla: {catalog}")
    c.expect("Disciplina já cursada ou aproveitada" in situation(catalog, "INTRO-A")["blockers"], "INTRO already done")
    await c.call("POST", f"{base}/offerings/{off['AVANC-A']}", 200, "carla takes AVANC", h["carla"])


async def check_office_and_closed_window(c: Checker, h: dict, ctx: dict, window_id: int) -> None:
    sec, off, ana_enrollment = h["secretaria"], ctx["offerings"], ctx["enrollments"]["ana"]
    office = f"/registration/program-enrollments/{ana_enrollment}"
    catalog = await c.call("GET", f"{office}/terms/{ctx['term']}/catalog", 200, "office catalog", sec)
    c.expect(catalog["window"] is None and catalog["max_credits"] is None, f"office catalog without window: {catalog}")
    await c.call("GET", f"{office}/terms/{ctx['term']}/catalog", 403, "student cannot use office catalog", h["ana"])
    await c.call("POST", f"{office}/offerings/{off['AVANC-A']}", 409, "office respects prerequisites", sec, json={})
    forced = await c.call("POST", f"{office}/offerings/{off['AVANC-A']}", 200, "office override", sec, json={"override": True})
    c.expect(forced.get("result") == "enrolled", f"override: {forced}")
    await c.call("DELETE", f"{office}/offerings/{off['AVANC-A']}", 204, "office drop", sec)

    await c.call("PATCH", f"/registration/windows/{window_id}", 200, "close window", sec,
                 json={"opens_at": iso(-timedelta(days=3)), "closes_at": iso(-timedelta(minutes=1))})
    base = f"/registration/my/windows/{window_id}"
    await c.call("POST", f"{base}/offerings/{off['ELET-A']}", 409, "closed window refuses", h["ana"])
    await c.call("DELETE", f"{base}/offerings/{off['ETICA-B']}", 409, "closed window refuses drop", h["ana"])
    windows = await c.call("GET", "/registration/my/windows", 200, "no open windows", h["ana"])
    c.expect(windows == [], f"closed window hidden: {windows}")
    listed = await c.call("GET", "/registration/windows", 200, "office lists windows", sec, params={"term_id": ctx["term"]})
    c.expect(len(listed) == 1 and listed[0]["is_open"] is False, f"listed: {listed}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        ctx["ids"] = ids
        window_id = await check_setup_permissions(c, h, ctx)
        await check_student_registration(c, h, ctx, window_id)
        await check_prior_approval(c, h, ctx, window_id)
        await check_office_and_closed_window(c, h, ctx, window_id)

    if c.failures:
        print("Registration flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Registration flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
