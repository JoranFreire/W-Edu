"""Exercise the user dossier: student with guardians, program enrollment, courses, finance and occurrences; guardian with
dependents; sections hidden without permission (coordinator without finance, company manager); scope and tenant isolation.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_dossier_check_{os.getpid()}.sqlite3"
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
from app.models.institution import Institution, InstitutionMembership, InstitutionType
from datetime import datetime, timedelta, timezone

from app.models.academic import Curriculum, CurriculumStatus, Program, ProgramLevel, ProgramStatus
from app.models.academic_groups import ProgramEnrollment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.finance import Charge
from app.models.guardians import GuardianRelationship, StudentGuardian
from app.models.school_life import StudentOccurrence
from app.models.student import Organization, StudentProfile
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
    "escola-a": [("admin-a", UserRole.institution_admin), ("coord", UserRole.coordinator), ("prof", UserRole.instructor),
                 ("ana", UserRole.student), ("mae", UserRole.guardian), ("gestor", UserRole.company_manager)],
    "escola-b": [("admin-b", UserRole.institution_admin)],
}


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        for slug, users in USERS.items():
            institution = Institution(slug=slug, name=slug.title(), type=InstitutionType.school)
            db.add(institution)
            db.flush()
            ids[slug] = institution.id
            for name, role in users:
                user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
                db.add(user)
                db.flush()
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
                ids[name] = user.id
        db.commit()

    with SessionLocal() as db:
        bind_institution(db, ids["escola-a"])
        organization = Organization(name="Parceira")
        db.add(organization)
        db.flush()
        db.get(Student, ids["gestor"]).organization_id = organization.id
        db.add(StudentProfile(student_id=ids["ana"], phone="81 99999-0000", document="123"))
        db.add(StudentProfile(student_id=ids["mae"], phone="81 98888-0000"))
        db.add(StudentGuardian(student_id=ids["ana"], guardian_id=ids["mae"], relationship_kind=GuardianRelationship.mother,
                               is_financial=True, is_primary=True))
        program = Program(code="FUND", name="Fundamental", level=ProgramLevel.basic, duration_terms=9, status=ProgramStatus.active)
        db.add(program)
        db.flush()
        curriculum = Curriculum(program_id=program.id, version="1", status=CurriculumStatus.active)
        db.add(curriculum)
        db.flush()
        db.add(ProgramEnrollment(student_id=ids["ana"], program_id=program.id, curriculum_id=curriculum.id, registration_number="2026-0001"))
        course = Course(name="Robótica")
        db.add(course)
        db.flush()
        db.add(Enrollment(student_id=ids["ana"], course_id=course.id))
        now = datetime.now(timezone.utc)
        db.add_all([
            Charge(student_id=ids["ana"], payer_id=ids["mae"], amount_cents=45000, due_at=now - timedelta(days=5)),
            Charge(student_id=ids["ana"], payer_id=ids["mae"], amount_cents=45000, due_at=now + timedelta(days=25)),
            StudentOccurrence(student_id=ids["ana"], description="Chegou atrasada", occurred_on=now.date()),
        ])
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


async def check_admin_view(c: Checker, h: dict, ids: dict) -> None:
    dossier = await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 200, "admin student dossier", h["admin-a"])
    c.expect(dossier.get("contact", {}).get("phone") == "81 99999-0000", f"contact: {dossier.get('contact')}")
    guardians = dossier.get("guardians") or []
    c.expect(len(guardians) == 1 and guardians[0]["person"]["id"] == ids["mae"] and guardians[0]["is_financial"]
             and guardians[0]["relationship_kind"] == "mother" and guardians[0]["person"]["phone"] == "81 98888-0000", f"guardians: {guardians}")
    c.expect(dossier.get("dependents") is None, "student has no dependents section")
    enrollments = dossier.get("program_enrollments") or []
    c.expect(len(enrollments) == 1 and enrollments[0]["registration_number"] == "2026-0001", f"enrollments: {enrollments}")
    c.expect([course["course_name"] for course in dossier.get("courses", [])] == ["Robótica"], f"courses: {dossier.get('courses')}")
    finance = dossier.get("finance") or {}
    c.expect(finance.get("open_count") == 2 and finance.get("overdue_count") == 1 and finance.get("open_cents") == 90000
             and finance.get("next_due_at"), f"finance: {finance}")
    occurrences = dossier.get("occurrences") or {}
    c.expect(occurrences.get("total") == 1 and occurrences["recent"][0]["description"] == "Chegou atrasada", f"occurrences: {occurrences}")
    c.expect(dossier.get("teaching") is None, "student has no teaching section")

    guardian = await c.call("GET", f"/admin/users/{ids['mae']}/dossier", 200, "guardian dossier", h["admin-a"])
    dependents = guardian.get("dependents") or []
    c.expect(len(dependents) == 1 and dependents[0]["person"]["id"] == ids["ana"], f"dependents: {dependents}")
    c.expect((guardian.get("finance") or {}).get("open_count") == 2, f"guardian pays the charges: {guardian.get('finance')}")

    teacher = await c.call("GET", f"/admin/users/{ids['prof']}/dossier", 200, "teacher dossier", h["admin-a"])
    c.expect(teacher.get("teaching") == [], f"teacher teaching section: {teacher.get('teaching')}")


async def check_permissions(c: Checker, h: dict, ids: dict) -> None:
    coord = await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 200, "coordinator dossier", h["coord"])
    c.expect(coord.get("guardians") is not None and coord.get("program_enrollments") is not None, "coordinator sees family and academic")
    c.expect(coord.get("finance") is None, f"coordinator has no finance.access: {coord.get('finance')}")
    await c.call("GET", f"/admin/users/{ids['mae']}/dossier", 200, "coordinator can view guardian", h["coord"])

    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 403, "manager outside company", h["gestor"])
    own = await c.call("GET", f"/admin/users/{ids['gestor']}/dossier", 200, "manager own company", h["gestor"])
    c.expect(own.get("organization_name") == "Parceira", f"organization name: {own.get('organization_name')}")
    c.expect(own.get("guardians") is None and own.get("finance") is None and own.get("occurrences") is None, f"manager sections: {own}")

    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 403, "instructor cannot open dossier", h["prof"])
    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 404, "other institution", h["admin-b"])


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for users in USERS.values() for name, _ in users}
        await check_admin_view(c, h, ids)
        await check_permissions(c, h, ids)

    if c.failures:
        print("User dossier flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("User dossier flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
