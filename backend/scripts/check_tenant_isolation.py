"""Exercise multi-tenant isolation through real FastAPI requests and real JWTs.

Uses a temporary database (SQLite by default; set DATABASE_URL to run against
PostgreSQL) and does not override authentication.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_tenant_check_{os.getpid()}.sqlite3"
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
from app.models.attendance import Attendance
from app.models.institution import Institution, InstitutionMembership
from app.models.session import Session as VoiceSession
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


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        inst_a = Institution(slug="escola-a", name="Escola A")
        inst_b = Institution(slug="faculdade-b", name="Faculdade B")
        db.add_all([inst_a, inst_b])
        db.flush()
        users = [
            (Student(name="Admin A", email="admin-a@example.com", password_hash=hash_password(PASSWORD), role=UserRole.admin), [inst_a]),
            (Student(name="Admin B", email="admin-b@example.com", password_hash=hash_password(PASSWORD), role=UserRole.institution_admin), [inst_b]),
            (Student(name="Aluno A", email="aluno-a@example.com", password_hash=hash_password(PASSWORD), role=UserRole.student), [inst_a]),
            (Student(name="Professor AB", email="prof@example.com", password_hash=hash_password(PASSWORD), role=UserRole.instructor), [inst_a, inst_b]),
            (Student(name="Root", email="root@example.com", password_hash=hash_password(PASSWORD), role=UserRole.super_admin), []),
            (Student(name="Instrutor A", email="instr-a@example.com", password_hash=hash_password(PASSWORD), role=UserRole.instructor), [inst_a]),
        ]
        for user, institutions in users:
            db.add(user)
            db.flush()
            for institution in institutions:
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=user.role))
        db.commit()


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, email: str, institution: str | None = None) -> dict:
        payload = {"email": email, "password": PASSWORD}
        if institution:
            payload["institution"] = institution
        response = await self.client.post("/auth/login", json=payload)
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def run() -> int:
    seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        admin_a = await c.login("admin-a@example.com")
        admin_b = await c.login("admin-b@example.com")

        r = await client.post("/courses", json={"name": "Matematica A"}, headers=admin_a)
        c.expect(r.status_code == 201, f"admin A create course: {r.status_code} {r.text}")
        course_a = r.json().get("id")
        r = await client.post("/courses", json={"name": "Direito B"}, headers=admin_b)
        c.expect(r.status_code == 201, f"admin B create course: {r.status_code}")
        course_b = r.json().get("id")

        r = await client.get("/courses", headers=admin_a)
        c.expect([x["name"] for x in r.json()] == ["Matematica A"], f"A lists only own courses: {r.json()}")
        r = await client.get("/courses", headers=admin_b)
        c.expect([x["name"] for x in r.json()] == ["Direito B"], f"B lists only own courses: {r.json()}")
        r = await client.get(f"/courses/{course_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A course by id: {r.status_code}")
        r = await client.delete(f"/courses/{course_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot delete A course: {r.status_code}")

        r = await client.get("/courses", headers={**admin_a, "X-Institution": "faculdade-b"})
        c.expect(r.status_code == 403, f"A admin cannot switch to B via header: {r.status_code}")

        r = await client.get("/admin/users", headers=admin_b)
        emails = sorted(x["email"] for x in r.json())
        c.expect(emails == ["admin-b@example.com", "prof@example.com", "root@example.com"], f"B lists only own users: {emails}")

        for headers in (admin_a, admin_b):
            r = await client.post("/admin/organizations", json={"name": "Acme"}, headers=headers)
            c.expect(r.status_code == 201, f"same organization name per tenant: {r.status_code} {r.text}")

        r = await client.post(
            "/admin/users",
            json={"name": "Novo", "email": "novo@example.com", "password": PASSWORD, "role": "super_admin"},
            headers=admin_b,
        )
        c.expect(r.status_code == 403, f"institution admin cannot create super admin: {r.status_code}")
        r = await client.post(
            "/admin/users",
            json={"name": "Novo", "email": "novo@example.com", "password": PASSWORD, "role": "student"},
            headers=admin_b,
        )
        c.expect(r.status_code == 201, f"institution admin creates student: {r.status_code} {r.text}")
        r = await client.get("/auth/institutions", headers=await c.login("novo@example.com"))
        c.expect([m["institution"]["slug"] for m in r.json()] == ["faculdade-b"], f"new user member of B: {r.json()}")

        prof = await c.login("prof@example.com")
        r = await client.get("/auth/institutions", headers=prof)
        c.expect(len(r.json()) == 2, f"professor has two memberships: {r.json()}")
        r = await client.post("/auth/switch-institution", json={"institution": "faculdade-b"}, headers=prof)
        c.expect(r.status_code == 200 and r.json()["institution"]["slug"] == "faculdade-b", f"professor switch: {r.text}")
        prof_b = {"Authorization": f"Bearer {r.json()['access_token']}"}
        r = await client.get("/courses", headers=prof_b)
        c.expect([x["name"] for x in r.json()] == ["Direito B"], f"switched token sees B: {r.json()}")

        r = await client.post(
            "/users",
            json={"name": "Publico", "email": "pub@example.com", "password": PASSWORD, "role": "admin"},
            headers={"X-Institution": "escola-a"},
        )
        c.expect(r.status_code == 201 and r.json()["role"] == "student", f"public signup forced to student: {r.text}")

        root = await c.login("root@example.com")
        r = await client.post(
            "/platform/institutions",
            json={
                "slug": "tecnico-c",
                "name": "Tecnico C",
                "type": "vocational",
                "admin": {"name": "Admin C", "email": "admin-c@example.com", "password": PASSWORD},
            },
            headers=root,
        )
        c.expect(r.status_code == 201, f"super admin creates institution: {r.status_code} {r.text}")
        admin_c = await c.login("admin-c@example.com")
        r = await client.get("/institutions/current", headers=admin_c)
        c.expect(r.json().get("slug") == "tecnico-c", f"admin C lands on C: {r.json()}")
        r = await client.get("/courses", headers=admin_c)
        c.expect(r.json() == [], f"new institution starts empty: {r.json()}")
        r = await client.get("/platform/institutions", headers=admin_a)
        c.expect(r.status_code == 403, f"institution admin blocked from platform: {r.status_code}")
        r = await client.get("/courses", headers={**root, "X-Institution": "escola-a"})
        c.expect([x["name"] for x in r.json()] == ["Matematica A"], f"super admin can enter any tenant: {r.json()}")

        r = await client.post("/institutions/campuses", json={"name": "Campus Centro"}, headers=admin_a)
        c.expect(r.status_code == 201, f"create campus: {r.status_code} {r.text}")
        campus_a = r.json().get("id")
        r = await client.post("/schedule/locations", json={"name": "Predio 1", "campus_id": campus_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot use A campus: {r.status_code}")
        r = await client.post("/schedule/locations", json={"name": "Predio 1", "campus_id": campus_a}, headers=admin_a)
        c.expect(r.status_code == 201, f"A location on A campus: {r.status_code} {r.text}")

        # Tabelas filhas: acesso por id e referencias cruzadas.
        r = await client.post("/lessons", json={"course_id": course_a, "title": "Aula A"}, headers=admin_a)
        c.expect(r.status_code == 201, f"admin A create lesson: {r.status_code} {r.text}")
        lesson_a = r.json().get("id")
        r = await client.get(f"/lessons/{lesson_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A lesson by id: {r.status_code}")
        r = await client.get(f"/lessons/course/{course_a}", headers=admin_b)
        c.expect(r.status_code == 404 or r.json() == [], f"B cannot list A lessons: {r.status_code} {r.text}")
        r = await client.patch(f"/lessons/{lesson_a}", json={"title": "Invadida"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot edit A lesson: {r.status_code}")
        r = await client.post("/lessons", json={"course_id": course_a, "title": "Intrusa"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot attach lesson to A course: {r.status_code} {r.text}")
        r = await client.post("/courses/{}/modules".format(course_a), json={"title": "Intruso"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot add module to A course: {r.status_code} {r.text}")

        with SessionLocal() as db:
            instr_a = db.query(Student).filter(Student.email == "instr-a@example.com").one().id
        class_payload = {
            "name": "Turma",
            "starts_at": "2027-02-01T08:00:00Z",
            "ends_at": "2027-06-30T12:00:00Z",
            "capacity": 30,
        }
        r = await client.post("/schedule/classes", json={**class_payload, "course_id": course_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot open class on A course: {r.status_code} {r.text}")
        r = await client.post(
            "/schedule/classes",
            json={**class_payload, "course_id": course_b, "instructor_id": instr_a},
            headers=admin_b,
        )
        c.expect(r.status_code == 404, f"B cannot assign A-only instructor: {r.status_code} {r.text}")
        r = await client.post(
            "/schedule/classes",
            json={**class_payload, "course_id": course_a, "instructor_id": instr_a},
            headers=admin_a,
        )
        c.expect(r.status_code == 201, f"A opens class with own instructor: {r.status_code} {r.text}")

        r = await client.post(
            f"/users/{instr_a}/availability",
            json={"day_of_week": 1, "start_time": "08:00", "end_time": "12:00"},
            headers=await c.login("instr-a@example.com"),
        )
        c.expect(r.status_code == 201, f"instructor adds availability: {r.status_code} {r.text}")
        availability_id = r.json().get("id")
        r = await client.patch(f"/users/availability/{availability_id}", json={"end_time": "13:00"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot edit A instructor availability: {r.status_code}")

        # Webhook sem usuario logado: registros herdam a instituicao da aula.
        with SessionLocal() as db:
            aluno_a = db.query(Student).filter(Student.email == "aluno-a@example.com").one().id
            db.add(VoiceSession(student_id=aluno_a, lesson_id=lesson_a, bevox_session_id="bv-1"))
            db.commit()
        r = await client.post("/webhooks/bevox/session-ended", json={"bevox_session_id": "bv-1", "transcript": "ok"})
        c.expect(r.status_code == 200, f"bevox webhook: {r.status_code} {r.text}")
        with SessionLocal() as db:
            institution_a = db.query(Institution).filter(Institution.slug == "escola-a").one().id
            attendance = db.query(Attendance).filter(Attendance.lesson_id == lesson_a).one()
            c.expect(attendance.institution_id == institution_a, f"webhook attendance tenant: {attendance.institution_id}")

    if c.failures:
        print("Tenant isolation check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Tenant isolation check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
