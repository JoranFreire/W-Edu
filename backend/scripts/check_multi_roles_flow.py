"""Exercise multiple roles: the same person as student and instructor in one institution, different roles per
institution, program enrollment granting the student role, role changes, coordinator limits and the super admin boundary.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_multi_roles_check_{os.getpid()}.sqlite3"
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
from app.core.tenancy import bind_institution
from app.models.institution import Institution, InstitutionMembership, InstitutionType
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
USERS = {
    "escola-a": [("admin-a", UserRole.institution_admin), ("coord", UserRole.coordinator), ("multi", UserRole.instructor)],
    "escola-b": [("admin-b", UserRole.institution_admin)],
}


def seed() -> dict[str, str]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        for slug, users in USERS.items():
            institution = Institution(slug=slug, name=slug.title(), type=InstitutionType.university)
            db.add(institution)
            db.flush()
            ids[slug] = str(institution.id)
            for name, role in users:
                user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
                db.add(user)
                db.flush()
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
                ids[name] = str(user.id)
        # A mesma pessoa: professora na escola A e aluna (pos-graduacao) na escola B.
        db.add(InstitutionMembership(institution_id=ids["escola-b"], user_id=ids["multi"], role=UserRole.student))
        db.commit()
    return ids


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, email: str, institution: str | None = None) -> dict:
        body = {"email": email, "password": PASSWORD, **({"institution": institution} if institution else {})}
        response = await self.client.post("/auth/login", json=body)
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


async def check_roles_per_institution(c: Checker) -> None:
    in_a = await c.call("GET", "/access/me", 200, "roles in A", await c.login("multi@example.com", "escola-a"))
    in_b = await c.call("GET", "/access/me", 200, "roles in B", await c.login("multi@example.com", "escola-b"))
    c.expect(in_a.get("roles") == ["instructor"] and "teaching.access" in in_a.get("permissions", []), f"A: {in_a}")
    c.expect(in_b.get("roles") == ["student"] and "teaching.access" not in in_b.get("permissions", []), f"B: {in_b}")


async def check_student_and_teacher(c: Checker, h: dict, ids: dict) -> None:
    admin = h["admin-a"]
    both = await c.call("POST", "/admin/users", 201, "create student and instructor", admin,
                        json={"name": "Dupla", "email": "dupla@example.com", "password": PASSWORD, "role": "instructor",
                              "roles": ["instructor", "student"]})
    c.expect(both.get("role") == "instructor" and both.get("roles") == ["instructor", "student"], f"created: {both}")
    listed = {user["email"]: user["roles"] for user in await c.call("GET", "/admin/users", 200, "list users", admin)}
    c.expect(listed.get("dupla@example.com") == ["instructor", "student"], f"listed roles: {listed}")
    students = [person["id"] for person in await c.call("GET", "/secretariat/students", 200, "secretariat students", admin)]
    advisors = [person["id"] for person in await c.call("GET", "/completion/advisors", 200, "advisors", admin)]
    c.expect(both["id"] in students and both["id"] in advisors, "same person is student and advisor")
    dupla = await c.login("dupla@example.com")
    access = await c.call("GET", "/access/me", 200, "dupla access", dupla)
    c.expect("teaching.access" in access.get("permissions", []) and set(access.get("roles", [])) == {"instructor", "student"}, f"dupla: {access}")
    await c.call("GET", "/assessment/teaching/offerings", 200, "dupla teaches", dupla)
    await c.call("GET", "/notifications/me", 200, "dupla inbox", dupla)

    # Matricula num programa da o papel de aluno a quem so era professor.
    program = await c.call("POST", "/academic/programs", 201, "program", admin, json={"code": "MBA", "name": "MBA", "level": "graduate", "duration_terms": 2})
    subject = await c.call("POST", "/academic/subjects", 201, "subject", admin, json={"code": "GES", "name": "Gestão", "hours": 30, "credits": 2})
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", admin, json={"version": "1"})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, "component", admin, json={"subject_id": subject["id"], "term_number": 1})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", admin)
    await c.call("POST", "/academic/program-enrollments", 201, "enroll the teacher", admin, json={"student_id": ids["multi"], "program_id": program["id"]})
    multi = await c.call("GET", "/access/me", 200, "multi after enrollment", await c.login("multi@example.com", "escola-a"))
    c.expect(set(multi.get("roles", [])) == {"instructor", "student"} and multi["roles"][0] == "instructor", f"enrolled teacher: {multi}")

    # Troca de papeis: deixa de ser aluno; o principal continua.
    changed = await c.call("PATCH", f"/admin/users/{both['id']}", 200, "drop student role", admin, json={"roles": ["instructor"]})
    c.expect(changed.get("roles") == ["instructor"], f"changed: {changed}")
    students = [person["id"] for person in await c.call("GET", "/secretariat/students", 200, "students after change", admin)]
    c.expect(both["id"] not in students, "no longer a student")


async def check_limits(c: Checker, h: dict) -> None:
    coord, admin = h["coord"], h["admin-a"]
    await c.call("POST", "/admin/users", 403, "coordinator cannot grant secretary", coord,
                 json={"name": "X", "email": "x@example.com", "password": PASSWORD, "roles": ["student", "secretary"]})
    ok = await c.call("POST", "/admin/users", 201, "coordinator creates student+instructor", coord,
                      json={"name": "Y", "email": "y@example.com", "password": PASSWORD, "roles": ["student", "instructor"]})
    c.expect(ok.get("role") == "student" and ok.get("roles") == ["student", "instructor"], f"primary is first: {ok}")
    staff = await c.call("POST", "/admin/users", 201, "admin creates student+secretary", admin,
                         json={"name": "Z", "email": "z@example.com", "password": PASSWORD, "roles": ["secretary", "student"]})
    await c.call("PATCH", f"/admin/users/{staff['id']}", 403, "coordinator cannot edit secretary-student", coord, json={"name": "Zeta"})
    await c.call("POST", "/admin/users", 403, "admin cannot grant super admin", admin,
                 json={"name": "S", "email": "s@example.com", "password": PASSWORD, "roles": ["student", "super_admin"]})
    await c.call("PATCH", f"/admin/users/{ok['id']}", 403, "coordinator cannot add admin role", coord, json={"roles": ["student", "institution_admin"]})


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com", slug) for slug, users in USERS.items() for name, _ in users}
        await check_roles_per_institution(c)
        await check_student_and_teacher(c, h, ids)
        await check_limits(c, h)

    if c.failures:
        print("Multi-role flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Multi-role flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
