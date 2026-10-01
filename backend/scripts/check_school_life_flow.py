"""Exercise school life (phase 15, delivery 2): occurrences, class agenda and the guardian portal view.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_school_life_check_{os.getpid()}.sqlite3"
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
    ("secretaria", UserRole.secretary),
    ("prof", UserRole.instructor),
    ("outro", UserRole.instructor),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
    ("carla", UserRole.student),
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

    async def login(self, email: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


async def setup_structure(c: Checker, h: dict, ids: dict) -> dict[str, int]:
    """Turma-grupo 6A (Ana e Bia), turma 7A vazia, oferta de 6A ministrada por 'prof' e responsavel Maria de Ana."""
    coord = h["coord"]
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    program = await c.call("POST", "/academic/programs", 201, "program", coord, json={"code": "EF", "name": "Fundamental", "level": "basic"})
    subject = await c.call("POST", "/academic/subjects", 201, "subject", coord, json={"code": "MAT", "name": "Matemática", "hours": 160})
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, "component", coord, json={"subject_id": subject["id"], "term_number": 6})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    group = await c.call("POST", "/academic/class-groups", 201, "group", coord, json={"program_id": program["id"], "term_id": term["id"], "name": "6A"})
    other = await c.call("POST", "/academic/class-groups", 201, "other group", coord, json={"program_id": program["id"], "term_id": term["id"], "name": "7A"})
    for name in ("ana", "bia"):
        enrollment = await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                  json={"student_id": ids[name], "program_id": program["id"]})
        await c.call("POST", f"/academic/class-groups/{group['id']}/members", 201, f"allocate {name}", coord,
                     json={"program_enrollment_id": enrollment["id"]})
    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Matemática EAD"})
    offering = await c.call("POST", "/schedule/classes", 201, "offering", coord, json={
        "course_id": course["id"], "name": "Matemática 6A", "capacity": 40, "instructor_id": ids["prof"],
        "starts_at": "2027-02-01T07:00:00Z", "ends_at": "2027-12-15T12:00:00Z", "class_group_id": group["id"],
    })
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "guardian of ana", h["secretaria"],
                 json={"name": "Maria", "email": "maria@example.com", "password": PASSWORD, "relationship_kind": "mother"})
    return {"group": group["id"], "other_group": other["id"], "offering": offering["id"]}


async def check_occurrences(c: Checker, h: dict, ids: dict, ctx: dict) -> dict[str, int]:
    prof, coord = h["prof"], h["coord"]
    occurrence = {"student_id": ids["ana"], "class_group_id": ctx["group"], "kind": "behavior", "severity": "medium",
                  "description": "Conversa excessiva durante a aula", "occurred_on": "2027-03-10"}
    registered = await c.call("POST", "/school/occurrences", 201, "instructor registers occurrence", prof, json=occurrence)
    c.expect(registered.get("reported_by", {}).get("name") == "Prof" and registered.get("acknowledged_at") is None, f"occurrence: {registered}")
    merit = await c.call("POST", "/school/occurrences", 201, "secretary registers merit", h["secretaria"],
                         json={"student_id": ids["ana"], "kind": "merit", "description": "Ajudou colegas", "occurred_on": "2027-03-12"})
    await c.call("POST", "/school/occurrences", 404, "unknown student", prof, json={**occurrence, "student_id": ids["prof"]})
    await c.call("POST", "/school/occurrences", 404, "unknown group", prof, json={**occurrence, "class_group_id": 9999})
    await c.call("POST", "/school/occurrences", 403, "student cannot register", h["ana"], json=occurrence)

    listed = await c.call("GET", f"/school/students/{ids['ana']}/occurrences", 200, "list occurrences", coord)
    c.expect([o["kind"] for o in listed] == ["merit", "behavior"], f"newest first: {listed}")
    await c.call("GET", f"/school/students/{ids['ana']}/occurrences", 403, "guardian uses the portal", await c.login("maria@example.com"))

    await c.call("DELETE", f"/school/occurrences/{registered['id']}", 403, "other instructor cannot remove", h["outro"])
    temp = await c.call("POST", "/school/occurrences", 201, "occurrence to remove", h["outro"],
                        json={"student_id": ids["bia"], "description": "Sem material", "kind": "material"})
    await c.call("DELETE", f"/school/occurrences/{temp['id']}", 204, "author removes", h["outro"])
    return {"behavior": registered["id"], "merit": merit["id"]}


async def check_agenda(c: Checker, h: dict, ids: dict, ctx: dict) -> None:
    prof, group = h["prof"], ctx["group"]
    path = f"/school/class-groups/{group}/agenda"
    homework = await c.call("POST", path, 201, "instructor publishes homework", prof, json={
        "kind": "homework", "title": "Exercícios p. 42", "due_on": "2027-03-15", "class_offering_id": ctx["offering"]})
    c.expect(homework.get("class_group_name") == "6A" and homework.get("class_offering_name") == "Matemática 6A", f"agenda item: {homework}")
    await c.call("POST", path, 201, "coordination publishes event", h["coord"], json={"kind": "event", "title": "Feira de ciências", "due_on": "2027-03-20"})
    await c.call("POST", path, 201, "past notice", h["secretaria"], json={"kind": "notice", "title": "Reunião", "due_on": "2027-02-10"})
    await c.call("POST", path, 403, "instructor outside the group", h["outro"], json={"title": "X", "due_on": "2027-03-15"})
    await c.call("POST", f"/school/class-groups/{ctx['other_group']}/agenda", 400, "offering of another group", h["coord"],
                 json={"title": "X", "due_on": "2027-03-15", "class_offering_id": ctx["offering"]})
    await c.call("POST", "/school/class-groups/9999/agenda", 404, "unknown group", h["coord"], json={"title": "X", "due_on": "2027-03-15"})

    upcoming = await c.call("GET", path, 200, "group agenda from date", prof, params={"from_date": "2027-03-01"})
    c.expect([i["title"] for i in upcoming] == ["Exercícios p. 42", "Feira de ciências"], f"agenda ordered by date: {upcoming}")
    mine = await c.call("GET", "/school/my/agenda", 200, "student agenda", h["bia"])
    c.expect(len(mine) == 3, f"student sees group agenda: {mine}")
    none = await c.call("GET", "/school/my/agenda", 200, "student outside groups", h["carla"])
    c.expect(none == [], f"no group, no agenda: {none}")
    await c.call("DELETE", f"/school/agenda/{homework['id']}", 403, "other instructor cannot remove", h["outro"])


async def check_portal(c: Checker, ids: dict, occ: dict) -> None:
    maria = await c.login("maria@example.com")
    base = f"/guardians/me/dependents/{ids['ana']}"
    occurrences = await c.call("GET", f"{base}/occurrences", 200, "dependent occurrences", maria)
    c.expect(len(occurrences) == 2, f"guardian sees occurrences: {occurrences}")
    acked = await c.call("POST", f"{base}/occurrences/{occ['behavior']}/acknowledge", 200, "acknowledge", maria)
    c.expect(acked.get("acknowledged_at") is not None, f"acknowledged: {acked}")
    again = await c.call("POST", f"{base}/occurrences/{occ['behavior']}/acknowledge", 200, "acknowledge twice", maria)
    c.expect(again.get("acknowledged_at") == acked.get("acknowledged_at"), "first acknowledgement is kept")
    await c.call("GET", f"/guardians/me/dependents/{ids['bia']}/occurrences", 404, "unlinked student", maria)
    await c.call("POST", f"/guardians/me/dependents/{ids['bia']}/occurrences/{occ['behavior']}/acknowledge", 404, "unlinked acknowledge", maria)

    agenda = await c.call("GET", f"{base}/agenda", 200, "dependent agenda", maria, params={"from_date": "2027-03-01"})
    c.expect([i["kind"] for i in agenda] == ["homework", "event"], f"dependent agenda: {agenda}")
    notices = await c.call("GET", f"{base}/notices", 200, "dependent notices", maria)
    titles = [n["title"] for n in notices]
    c.expect(titles.count("Nova ocorrência") == 2 and titles.count("Agenda da turma") == 3, f"family notices: {titles}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        occ = await check_occurrences(c, h, ids, ctx)
        await check_agenda(c, h, ids, ctx)
        await check_portal(c, ids, occ)

    if c.failures:
        print("School life flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("School life flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
