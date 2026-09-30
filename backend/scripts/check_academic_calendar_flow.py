"""Exercise academic terms, calendar, program enrollment and class groups (phase 12, delivery 2).

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_calendar_check_{os.getpid()}.sqlite3"
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
from app.models.institution import Institution, InstitutionMembership
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
    ("admin", UserRole.institution_admin),
    ("prof", UserRole.instructor),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
    ("caio", UserRole.student),
)


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola")
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

    async def login(self, name: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": f"{name}@example.com", "password": PASSWORD})
        assert response.status_code == 200, f"login {name}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def status(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs) -> dict:
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


def expected_school_days(start: date, end: date, closed: set[date], extra: set[date]) -> int:
    days = [start + timedelta(days=n) for n in range((end - start).days + 1)]
    return sum(1 for day in days if (day.weekday() < 5 and day not in closed) or day in extra)


async def check_terms(c: Checker, coord: dict, admin: dict) -> int:
    term = await c.status("POST", "/academic/terms", 201, "create term", coord,
                          json={"name": "2027", "kind": "year", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    await c.status("POST", "/academic/terms", 409, "duplicate term name", coord,
                   json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    await c.status("POST", "/academic/terms", 422, "term ending before start", coord,
                   json={"name": "x", "starts_on": "2027-02-01", "ends_on": "2027-01-01"})
    term_id = term["id"]

    periods = f"/academic/terms/{term_id}/grading-periods"
    for n, (start, end) in enumerate((("2027-02-01", "2027-04-30"), ("2027-05-01", "2027-07-09"),
                                      ("2027-07-26", "2027-09-30"), ("2027-10-01", "2027-12-15")), start=1):
        created = await c.status("POST", periods, 201, f"bimestre {n}", coord, json={"name": f"{n}º bimestre", "starts_on": start, "ends_on": end})
        c.expect(created.get("order") == n, f"automatic order {n}: {created.get('order')}")
    await c.status("POST", periods, 400, "overlapping grading period", coord,
                   json={"name": "extra", "starts_on": "2027-04-01", "ends_on": "2027-05-10"})
    await c.status("POST", periods, 400, "grading period outside term", coord,
                   json={"name": "fora", "starts_on": "2027-12-10", "ends_on": "2027-12-31"})

    events = [
        {"kind": "holiday", "title": "Tiradentes", "starts_on": "2027-04-21", "term_id": term_id},
        {"kind": "recess", "title": "Recesso", "starts_on": "2027-07-12", "ends_on": "2027-07-23", "term_id": term_id},
        {"kind": "school_day", "title": "Sábado letivo", "starts_on": "2027-03-06", "term_id": term_id},
        {"kind": "exam", "title": "Simulado", "starts_on": "2027-06-10", "term_id": term_id},
    ]
    for event in events:
        await c.status("POST", "/academic/calendar-events", 201, f"event {event['title']}", coord, json=event)
    await c.status("POST", "/academic/calendar-events", 400, "event outside term", coord,
                   json={"kind": "holiday", "title": "Fora", "starts_on": "2028-01-01", "term_id": term_id})
    summary = await c.status("GET", f"/academic/terms/{term_id}/calendar-summary", 200, "calendar summary", coord)
    recess = {date(2027, 7, 12) + timedelta(days=n) for n in range(12)}
    expected = expected_school_days(date(2027, 2, 1), date(2027, 12, 15), {date(2027, 4, 21)} | recess, {date(2027, 3, 6)})
    c.expect(summary == {"school_days": expected, "non_school_days": 11, "extra_school_days": 1, "exams": 1}, f"summary: {summary} (expected {expected} school days)")
    listed = await c.status("GET", "/academic/calendar-events", 200, "list events in range", coord,
                            params={"start": "2027-07-15", "end": "2027-07-31"})
    c.expect([e["title"] for e in listed] == ["Recesso"], f"range filter includes overlapping recess: {listed}")

    await c.status("POST", f"/academic/terms/{term_id}/status", 409, "planned cannot close directly", coord, json={"status": "closed"})
    await c.status("POST", f"/academic/terms/{term_id}/status", 200, "open term", coord, json={"status": "open"})
    return term_id


async def check_enrollments(c: Checker, coord: dict, ids: dict[str, int], term_id: int) -> tuple[int, dict[str, int]]:
    program = await c.status("POST", "/academic/programs", 201, "program", coord,
                             json={"code": "EF", "name": "Fundamental", "level": "basic", "duration_terms": 9})
    program_id = program["id"]
    await c.status("POST", "/academic/program-enrollments", 400, "program without active curriculum", coord,
                   json={"student_id": ids["ana"], "program_id": program_id})
    subject = await c.status("POST", "/academic/subjects", 201, "subject", coord, json={"code": "MAT6", "name": "Matemática", "hours": 160})
    curriculum = await c.status("POST", f"/academic/programs/{program_id}/curricula", 201, "curriculum", coord, json={"version": "2027"})
    await c.status("POST", f"/academic/curricula/{curriculum['id']}/components", 201, "component", coord,
                   json={"subject_id": subject["id"], "term_number": 6})
    await c.status("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate curriculum", coord)

    enrollments = {}
    for name in ("ana", "bia", "caio"):
        created = await c.status("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                 json={"student_id": ids[name], "program_id": program_id, "entry_term_id": term_id})
        enrollments[name] = created.get("id")
        c.expect(created.get("curriculum_id") == curriculum["id"], f"default curriculum is the active one: {created}")
    listed = await c.status("GET", "/academic/program-enrollments", 200, "list enrollments", coord, params={"program_id": program_id})
    c.expect([e["registration_number"] for e in listed] == ["2027EF0001", "2027EF0002", "2027EF0003"], f"registration numbers: {listed}")
    await c.status("POST", "/academic/program-enrollments", 409, "second open enrollment", coord,
                   json={"student_id": ids["ana"], "program_id": program_id})
    await c.status("POST", "/academic/program-enrollments", 409, "manual number collision", coord,
                   json={"student_id": ids["prof"], "program_id": program_id, "registration_number": "2027EF0001"})

    status_path = "/academic/program-enrollments/{}/status"
    await c.status("POST", status_path.format(enrollments["caio"]), 200, "lock enrollment", coord, json={"status": "locked"})
    await c.status("POST", status_path.format(enrollments["caio"]), 409, "locked cannot graduate", coord, json={"status": "graduated"})
    aluno = await c.login("ana")
    mine = await c.status("GET", "/academic/program-enrollments/me", 200, "student sees own enrollment", aluno)
    c.expect([e["registration_number"] for e in mine] == ["2027EF0001"], f"own enrollments only: {mine}")
    await c.status("GET", "/academic/program-enrollments", 403, "student cannot list enrollments", aluno)
    return program_id, enrollments


async def check_groups(c: Checker, coord: dict, admin: dict, ids: dict[str, int], term_id: int, program_id: int, enrollments: dict[str, int]) -> None:
    base = {"program_id": program_id, "term_id": term_id, "curriculum_term_number": 6, "shift": "morning"}
    await c.status("POST", "/academic/class-groups", 400, "homeroom must be a teacher", coord,
                   json={**base, "name": "6º X", "homeroom_teacher_id": ids["bia"]})
    await c.status("POST", "/academic/class-groups", 400, "term number beyond duration", coord,
                   json={**base, "name": "10º A", "curriculum_term_number": 10})
    group_a = await c.status("POST", "/academic/class-groups", 201, "group 6A", coord,
                             json={**base, "name": "6º A", "capacity": 1, "homeroom_teacher_id": ids["prof"]})
    group_b = await c.status("POST", "/academic/class-groups", 201, "group 6B", coord, json={**base, "name": "6º B"})
    await c.status("POST", "/academic/class-groups", 409, "duplicate group name in term", coord, json={**base, "name": "6º A"})

    members = "/academic/class-groups/{}/members"
    await c.status("POST", members.format(group_a["id"]), 201, "allocate ana", coord, json={"program_enrollment_id": enrollments["ana"]})
    await c.status("POST", members.format(group_a["id"]), 409, "group full", coord, json={"program_enrollment_id": enrollments["bia"]})
    await c.status("POST", members.format(group_b["id"]), 409, "one group per term", coord, json={"program_enrollment_id": enrollments["ana"]})
    await c.status("POST", members.format(group_b["id"]), 400, "locked enrollment not allocated", coord, json={"program_enrollment_id": enrollments["caio"]})
    await c.status("POST", members.format(group_b["id"]), 201, "allocate bia", coord, json={"program_enrollment_id": enrollments["bia"]})
    roster = await c.status("GET", members.format(group_a["id"]), 200, "roster", coord)
    c.expect([(m["registration_number"], m["student"]["name"]) for m in roster] == [("2027EF0001", "Ana")], f"roster: {roster}")
    groups = await c.status("GET", "/academic/class-groups", 200, "list groups", coord, params={"term_id": term_id})
    c.expect({g["name"]: g["member_count"] for g in groups} == {"6º A": 1, "6º B": 1}, f"member counts: {groups}")
    await c.status("DELETE", f"/academic/class-groups/{group_a['id']}", 409, "group with members", admin)

    course = await c.status("POST", "/courses", 201, "course", coord, json={"name": "Matemática EAD"})
    offering = {"course_id": course["id"], "name": "Matemática 6º A", "capacity": 30,
                "starts_at": "2027-02-01T07:00:00Z", "ends_at": "2027-12-15T12:00:00Z"}
    created = await c.status("POST", "/schedule/classes", 201, "offering linked to group", coord, json={**offering, "class_group_id": group_a["id"]})
    c.expect(created.get("term_id") == term_id, f"offering inherits group term: {created}")
    other_term = await c.status("POST", "/academic/terms", 201, "second term", coord,
                                json={"name": "2028", "starts_on": "2028-02-01", "ends_on": "2028-12-15"})
    await c.status("POST", "/schedule/classes", 400, "group from another term", coord,
                   json={**offering, "class_group_id": group_a["id"], "term_id": other_term["id"]})
    await c.status("DELETE", f"/academic/terms/{term_id}", 409, "open term cannot be deleted", admin)
    await c.status("DELETE", f"/academic/terms/{other_term['id']}", 204, "unused planned term deleted", admin)

    await c.status("POST", f"/academic/terms/{term_id}/status", 200, "close term", coord, json={"status": "closed"})
    periods = await c.status("GET", f"/academic/terms/{term_id}/grading-periods", 200, "periods after close", coord)
    c.expect({p["status"] for p in periods} == {"closed"}, f"closing term closes periods: {periods}")
    await c.status("PATCH", f"/academic/terms/{term_id}", 409, "closed term is read-only", coord, json={"name": "2027b"})
    await c.status("POST", members.format(group_b["id"]), 409, "no allocation in closed term", coord,
                   json={"program_enrollment_id": enrollments["ana"]})


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        coord, admin = await c.login("coord"), await c.login("admin")
        term_id = await check_terms(c, coord, admin)
        program_id, enrollments = await check_enrollments(c, coord, ids, term_id)
        await check_groups(c, coord, admin, ids, term_id, program_id, enrollments)

    if c.failures:
        print("Academic calendar flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Academic calendar flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
