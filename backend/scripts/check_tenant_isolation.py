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
os.environ.setdefault("DOCUMENTS_STORAGE_DIR", tempfile.mkdtemp(prefix="wedu_isolation_documents_"))
os.environ["TENANT_BASE_DOMAIN"] = "wedu.test"

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
from app.core.tenant_host import slug_from_host
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
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
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
        class_a = r.json().get("id")
        r = await client.post(f"/registration/offerings/{class_a}/time-slots", json={"weekday": 0, "starts_at": "08:00", "ends_at": "10:00"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot set A offering slots: {r.status_code}")
        r = await client.get(f"/registration/offerings/{class_a}/time-slots", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A offering slots: {r.status_code}")

        r = await client.post(
            f"/users/{instr_a}/availability",
            json={"day_of_week": 1, "start_time": "08:00", "end_time": "12:00"},
            headers=await c.login("instr-a@example.com"),
        )
        c.expect(r.status_code == 201, f"instructor adds availability: {r.status_code} {r.text}")
        availability_id = r.json().get("id")
        r = await client.patch(f"/users/availability/{availability_id}", json={"end_time": "13:00"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot edit A instructor availability: {r.status_code}")

        # Estrutura curricular: mesmo codigo por instituicao, sem referencias cruzadas.
        subject_ids = {}
        for key, headers in (("a", admin_a), ("b", admin_b)):
            r = await client.post("/academic/subjects", json={"code": "MAT1", "name": f"Matematica {key}"}, headers=headers)
            c.expect(r.status_code == 201, f"same subject code per tenant ({key}): {r.status_code} {r.text}")
            subject_ids[key] = r.json().get("id")
        r = await client.get(f"/academic/subjects/{subject_ids['a']}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A subject: {r.status_code}")
        r = await client.post(
            f"/academic/subjects/{subject_ids['b']}/prerequisites", json={"subject_id": subject_ids["a"]}, headers=admin_b
        )
        c.expect(r.status_code == 404, f"B cannot require A subject: {r.status_code}")
        r = await client.post("/academic/subjects", json={"code": "X", "name": "X", "course_id": course_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B subject cannot reuse A course: {r.status_code}")
        r = await client.post("/academic/programs", json={"code": "EF2", "name": "Fundamental II", "level": "basic"}, headers=admin_a)
        program_a = r.json().get("id")
        r = await client.post(f"/academic/programs/{program_a}/curricula", json={"version": "1"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot add curriculum to A program: {r.status_code}")
        r = await client.post("/academic/programs", json={"code": "DIR", "name": "Direito"}, headers=admin_b)
        r = await client.post(f"/academic/programs/{r.json().get('id')}/curricula", json={"version": "1"}, headers=admin_b)
        curriculum_b = r.json().get("id")
        r = await client.post(
            f"/academic/curricula/{curriculum_b}/components", json={"subject_id": subject_ids["a"], "term_number": 1}, headers=admin_b
        )
        c.expect(r.status_code == 404, f"B curriculum cannot use A subject: {r.status_code}")
        r = await client.get("/academic/programs", headers=admin_b)
        c.expect([p["code"] for p in r.json()] == ["DIR"], f"B lists only own programs: {r.json()}")

        # Periodos, turmas-grupo e matriculas no programa.
        term = {"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"}
        term_a = (await client.post("/academic/terms", json=term, headers=admin_a)).json().get("id")
        r = await client.post("/academic/terms", json=term, headers=admin_b)
        c.expect(r.status_code == 201, f"same term name per tenant: {r.status_code} {r.text}")
        r = await client.post(
            "/academic/calendar-events", json={"kind": "holiday", "title": "X", "starts_on": "2027-03-01", "term_id": term_a}, headers=admin_b
        )
        c.expect(r.status_code == 404, f"B cannot add event to A term: {r.status_code}")
        r = await client.post(
            "/academic/class-groups", json={"program_id": program_a, "term_id": term_a, "name": "6A"}, headers=admin_b
        )
        c.expect(r.status_code == 404, f"B cannot create group on A program/term: {r.status_code}")
        with SessionLocal() as db:
            aluno_a_id = db.query(Student).filter(Student.email == "aluno-a@example.com").one().id
        r = await client.post(
            "/academic/program-enrollments", json={"student_id": aluno_a_id, "program_id": program_a}, headers=admin_b
        )
        c.expect(r.status_code == 404, f"B cannot enroll A student in A program: {r.status_code}")
        r = await client.get("/academic/terms", headers=admin_a)
        c.expect(len(r.json()) == 1, f"A lists only own terms: {r.json()}")

        # Avaliacao e diario: esquemas por instituicao e ofertas de outra instituicao invisiveis.
        for headers in (admin_a, admin_b):
            r = await client.post("/assessment/grading-schemes", json={"name": "Padrão", "is_default": True}, headers=headers)
            c.expect(r.status_code == 201, f"same scheme name per tenant: {r.status_code} {r.text}")
        r = await client.get("/assessment/teaching/offerings", headers=admin_a)
        offering_a = r.json()[0]["id"] if r.status_code == 200 and r.json() else None
        c.expect(offering_a is not None, f"A has a teaching offering: {r.status_code} {r.text[:120]}")
        r = await client.get(f"/assessment/offerings/{offering_a}/gradebook", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A gradebook: {r.status_code}")
        r = await client.post(f"/assessment/offerings/{offering_a}/items", json={"name": "Invasora"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot add item to A offering: {r.status_code}")
        r = await client.post(f"/assessment/offerings/{offering_a}/diary", json={"date": "2027-03-01", "content_taught": "x"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot write A diary: {r.status_code}")
        r = await client.get("/assessment/grading-schemes", headers=admin_b)
        c.expect(len(r.json()) == 1, f"B lists only own schemes: {r.json()}")
        r = await client.get(f"/assessment/offerings/{offering_a}/results", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A results: {r.status_code}")
        r = await client.post(f"/assessment/offerings/{offering_a}/finalize", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot finalize A offering: {r.status_code}")

        # Secretaria: matricula de A invisivel para B.
        subject_ef = (await client.post("/academic/subjects", json={"code": "EF1", "name": "EF"}, headers=admin_a)).json()["id"]
        curriculum_ef = (await client.post(f"/academic/programs/{program_a}/curricula", json={"version": "1"}, headers=admin_a)).json()["id"]
        await client.post(f"/academic/curricula/{curriculum_ef}/components", json={"subject_id": subject_ef, "term_number": 1}, headers=admin_a)
        await client.post(f"/academic/curricula/{curriculum_ef}/activate", headers=admin_a)
        r = await client.post("/academic/program-enrollments", json={"student_id": aluno_a_id, "program_id": program_a}, headers=admin_a)
        c.expect(r.status_code == 201, f"A enrolls own student: {r.status_code} {r.text}")
        enrollment_a = r.json().get("id")
        for path in ("transcript", "events"):
            r = await client.get(f"/secretariat/enrollments/{enrollment_a}/{path}", headers=admin_b)
            c.expect(r.status_code == 404, f"B cannot read A enrollment {path}: {r.status_code}")
        r = await client.post(f"/secretariat/enrollments/{enrollment_a}/lock", json={}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot lock A enrollment: {r.status_code}")
        r = await client.post(f"/secretariat/enrollments/{enrollment_a}/declarations", json={"kind": "enrollment"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot issue declaration for A: {r.status_code}")
        r = await client.post(f"/secretariat/enrollments/{enrollment_a}/declarations", json={"kind": "enrollment"}, headers=admin_a)
        declaration_a = r.json()
        r = await client.get(f"/secretariat/declarations/{declaration_a.get('id')}/pdf", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot download A declaration: {r.status_code}")
        r = await client.post(
            f"/guardians/students/{aluno_a_id}/links",
            json={"name": "Mãe", "email": "mae-a@example.com", "password": PASSWORD, "is_financial": True},
            headers=admin_b,
        )
        c.expect(r.status_code == 404, f"B cannot link guardian to A student: {r.status_code}")
        r = await client.get(f"/guardians/students/{aluno_a_id}/links", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot list A guardians: {r.status_code}")

        # Vida escolar: ocorrencias e agenda de A invisiveis para B.
        r = await client.post("/school/occurrences", json={"student_id": aluno_a_id, "description": "x"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot register occurrence for A student: {r.status_code}")
        r = await client.post("/school/occurrences", json={"student_id": aluno_a_id, "description": "Atraso", "kind": "lateness"}, headers=admin_a)
        occurrence_a = r.json().get("id")
        r = await client.get(f"/school/students/{aluno_a_id}/occurrences", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot list A occurrences: {r.status_code}")
        r = await client.delete(f"/school/occurrences/{occurrence_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot remove A occurrence: {r.status_code}")
        aluno_a_headers = await c.login("aluno-a@example.com")
        r = await client.get("/notifications/me", headers=aluno_a_headers)
        notice_a = next((n["id"] for n in r.json() if n["event_type"] == "occurrence_registered"), None)
        c.expect(notice_a is not None, f"A student inbox has the occurrence notice: {r.json()}")
        r = await client.post(f"/notifications/me/{notice_a}/read", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot mark A notice as read: {r.status_code}")
        r = await client.post("/academic/class-groups", json={"program_id": program_a, "term_id": term_a, "name": "6A"}, headers=admin_a)
        group_a = r.json().get("id")
        r = await client.post(f"/school/class-groups/{group_a}/agenda", json={"title": "Invasora", "due_on": "2027-03-01"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot publish on A agenda: {r.status_code}")
        r = await client.get(f"/school/class-groups/{group_a}/agenda", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A agenda: {r.status_code}")
        # Processo seletivo: edital de A invisivel para B, inclusive no catalogo publico de B.
        call = {"class_offering_id": class_a, "title": "Edital A", "seats": 1, "opens_at": "2020-01-01T00:00:00Z", "closes_at": "2099-01-01T00:00:00Z"}
        r = await client.post("/admissions/calls", json=call, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot open call on A class: {r.status_code}")
        r = await client.post("/admissions/calls", json=call, headers=admin_a)
        call_a = r.json().get("id")
        r = await client.post(f"/admissions/calls/{call_a}/status", json={"status": "open"}, headers=admin_a)
        r = await client.get("/admissions/public/calls", headers={"X-Institution": "faculdade-b"})
        c.expect(r.json() == [], f"B public catalog hides A calls: {r.json()}")
        r = await client.get("/admissions/public/calls", headers={"X-Institution": "escola-a"})
        c.expect([x["title"] for x in r.json()] == ["Edital A"], f"A public catalog: {r.json()}")
        r = await client.get(f"/admissions/public/calls/{call_a}", headers={"X-Institution": "faculdade-b"})
        c.expect(r.status_code == 404, f"A call not reachable through B: {r.status_code}")
        r = await client.post(f"/admissions/calls/{call_a}/select", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot run A selection: {r.status_code}")

        # Programas sociais: financiador, itens e frequencia de A invisiveis para B.
        r = await client.post("/social/funding-sources", json={"name": "Convenio A", "starts_on": "2027-01-01"}, headers=admin_a)
        funding_a = r.json().get("id")
        r = await client.get(f"/social/funding-sources/{funding_a}/report", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A funding report: {r.status_code}")
        r = await client.patch(f"/schedule/classes/{class_a}", json={"funding_source_id": funding_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot touch A class: {r.status_code}")
        r = await client.post("/schedule/classes", json={**class_payload, "course_id": course_b, "funding_source_id": funding_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot fund own class with A funding: {r.status_code}")
        r = await client.post("/social/benefit-items", json={"name": "Lanche A"}, headers=admin_a)
        item_a = r.json().get("id")
        r = await client.post(f"/social/benefit-items/{item_a}/stock", json={"quantity": 5, "received_on": "2027-01-01"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot add stock to A item: {r.status_code}")
        r = await client.get(f"/retention/offerings/{class_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A retention: {r.status_code}")

        # Almoxarifado: materiais e requisicoes de A invisiveis para B.
        r = await client.post("/warehouse/items", json={"name": "Papel A"}, headers=admin_a)
        material_a = r.json().get("id")
        r = await client.get("/warehouse/items", headers=admin_b)
        c.expect(r.json() == [], f"B lists no A materials: {r.json()}")
        r = await client.post(f"/warehouse/items/{material_a}/entries", json={"quantity": 5, "received_on": "2027-01-01"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot stock A material: {r.status_code}")
        r = await client.post("/warehouse/requests", json={"purpose": "X", "needed_on": "2027-01-01", "lines": [{"item_id": material_a, "quantity": 1}]}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot request A material: {r.status_code}")
        r = await client.post("/warehouse/requests", json={"purpose": "Aula", "needed_on": "2027-01-01", "lines": [{"item_id": material_a, "quantity": 1}]}, headers=admin_a)
        request_a = r.json().get("id")
        r = await client.post(f"/warehouse/requests/{request_a}/reject", json={"note": "x"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot reject A request: {r.status_code}")

        # Contratos: modelo e contrato de A invisiveis para B.
        r = await client.post("/contracts/templates", json={"name": "Contrato A", "body": "Contrato de {student_name}."}, headers=admin_a)
        template_a = r.json().get("id")
        r = await client.post(f"/contracts/enrollments/{enrollment_a}", json={"template_id": template_a}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot issue contract for A: {r.status_code}")
        r = await client.post(f"/contracts/enrollments/{enrollment_a}", json={"template_id": template_a}, headers=admin_a)
        contract_a = r.json().get("id")
        r = await client.get(f"/contracts/{contract_a}/pdf", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot download A contract: {r.status_code}")
        r = await client.post(f"/contracts/{contract_a}/cancel", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot cancel A contract: {r.status_code}")
        r = await client.get("/contracts/templates", headers=admin_b)
        c.expect(r.json() == [], f"B lists no A templates: {r.json()}")

        # Mensalidades: plano, descontos e extrato de A invisiveis para B.
        plan = {"name": "Mensalidade", "term_id": term_a, "program_id": program_a, "amount_cents": 1000, "first_due_on": "2027-02-10"}
        r = await client.post("/tuition/plans", json=plan, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot create plan on A term: {r.status_code}")
        r = await client.post("/tuition/plans", json=plan, headers=admin_a)
        plan_a = r.json().get("id")
        r = await client.post(f"/tuition/plans/{plan_a}/generate", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot generate A plan: {r.status_code}")
        r = await client.post(f"/tuition/plans/{plan_a}/generate", headers=admin_a)
        c.expect(r.json().get("created", 0) >= 1, f"A generates own plan: {r.text}")
        r = await client.get(f"/tuition/enrollments/{enrollment_a}/charges", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A statement: {r.status_code}")
        r = await client.get(f"/tuition/enrollments/{enrollment_a}/charges", headers=admin_a)
        charge_a = r.json()[0]["id"]
        r = await client.post(f"/tuition/charges/{charge_a}/settle", json={}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot settle A charge: {r.status_code}")
        r = await client.post(f"/tuition/enrollments/{enrollment_a}/discounts", json={"percent": 10, "valid_from": "2027-01-01"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot grant discount to A: {r.status_code}")
        r = await client.get("/tuition/plans", headers=admin_b)
        c.expect(r.json() == [], f"B lists no A plans: {r.json()}")

        # Requisitos de conclusao: estagio, TCC e integralizacao de A invisiveis para B.
        r = await client.post(f"/completion/enrollments/{enrollment_a}/internships", json={"company_name": "X", "starts_on": "2027-03-01"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot register internship for A: {r.status_code}")
        r = await client.post(f"/completion/enrollments/{enrollment_a}/internships", json={"company_name": "Empresa A", "starts_on": "2027-03-01"}, headers=admin_a)
        internship_a = r.json().get("id")
        r = await client.patch(f"/completion/internships/{internship_a}", json={"status": "cancelled"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot update A internship: {r.status_code}")
        r = await client.get(f"/completion/internships/{internship_a}/logs", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A internship logs: {r.status_code}")
        r = await client.put(f"/completion/enrollments/{enrollment_a}/final-project", json={"title": "Invasor"}, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot register A final project: {r.status_code}")
        r = await client.get(f"/completion/enrollments/{enrollment_a}/integralization", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A integralization: {r.status_code}")
        r = await client.get("/completion/advising", headers=admin_b)
        c.expect(r.json() == {"internships": [], "final_projects": []}, f"B advising shows no A records: {r.json()}")

        # Matricula por disciplina: janela e catalogo de A invisiveis para B.
        window = {"term_id": term_a, "name": "Janela", "opens_at": "2027-01-01T00:00:00Z", "closes_at": "2027-01-10T00:00:00Z"}
        r = await client.post("/registration/windows", json=window, headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot open window on A term: {r.status_code}")
        r = await client.post("/registration/windows", json=window, headers=admin_a)
        window_a = r.json().get("id")
        r = await client.get("/registration/windows", headers=admin_b)
        c.expect(r.json() == [], f"B lists no A windows: {r.json()}")
        r = await client.delete(f"/registration/windows/{window_a}", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot delete A window: {r.status_code}")
        r = await client.get(f"/registration/program-enrollments/{enrollment_a}/terms/{term_a}/catalog", headers=admin_b)
        c.expect(r.status_code == 404, f"B cannot read A registration catalog: {r.status_code}")
        r = await client.get(f"/secretariat/declarations/validate/{declaration_a.get('validation_code')}")
        c.expect(r.json().get("valid") is True and r.json().get("institution_name") == "Escola A", f"public validation names the issuer: {r.text}")

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

        # Instituicao pelo subdominio (TENANT_BASE_DOMAIN=wedu.test).
        host_b = {"Host": "faculdade-b.wedu.test"}
        r = await client.post("/auth/login", json={"email": "prof@example.com", "password": PASSWORD}, headers=host_b)
        prof_host_b = {"Authorization": f"Bearer {r.json()['access_token']}", **host_b}
        c.expect(r.json()["institution"]["slug"] == "faculdade-b", f"login on subdomain picks it: {r.json().get('institution')}")
        r = await client.get("/courses", headers=prof_host_b)
        c.expect([x["name"] for x in r.json()] == ["Direito B"], f"subdomain scopes requests: {r.json()}")
        r = await client.get("/courses", headers={**admin_a, "X-Forwarded-Host": "faculdade-b.wedu.test"})
        c.expect(r.status_code == 403, f"admin A blocked on B subdomain: {r.status_code}")
        r = await client.get("/institutions/public", headers={"X-Forwarded-Host": "escola-a.wedu.test:443"})
        c.expect(r.status_code == 200 and r.json()["slug"] == "escola-a", f"public branding by host: {r.text}")
        r = await client.get("/institutions/public")
        c.expect(r.status_code == 404, f"no public branding without subdomain: {r.status_code}")
        r = await client.post(
            "/users",
            json={"name": "Via host", "email": "host@example.com", "password": PASSWORD},
            headers={"Host": "faculdade-b.wedu.test"},
        )
        c.expect(r.status_code == 201, f"public signup on subdomain: {r.status_code} {r.text}")
        r = await client.get("/auth/institutions", headers=await c.login("host@example.com"))
        c.expect([m["institution"]["slug"] for m in r.json()] == ["faculdade-b"], f"signup joins subdomain institution: {r.json()}")
        for host, expected in [
            ("escola-a.wedu.test", "escola-a"), ("ESCOLA-A.wedu.test:8080", "escola-a"), ("www.wedu.test", None),
            ("wedu.test", None), ("a.b.wedu.test", None), ("escola-a.outro.test", None), (None, None),
        ]:
            c.expect(slug_from_host(host) == expected, f"slug_from_host({host!r}) -> {slug_from_host(host)!r}")

    if c.failures:
        print("Tenant isolation check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Tenant isolation check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
