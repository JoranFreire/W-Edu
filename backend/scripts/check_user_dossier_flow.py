"""Exercise the user dossier: student with guardians, program enrollment, courses, finance and occurrences; guardian with
dependents; completed courses, benefits received, materials received and statement; sections hidden without permission (coordinator without finance, company manager); scope and tenant isolation.

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

from scripts.check_support import ApiClient  # noqa: E402
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
from app.models.lesson import Lesson
from app.models.progress import Progress, ProgressStatus
from app.models.schedule import ClassOffering
from app.models.social_programs import BenefitDelivery, BenefitItem
from app.models.student import Organization, StudentProfile
from app.models.warehouse import MaterialRequest, MaterialRequestLine, RequestStatus, WarehouseItem
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
            ids[slug] = str(institution.id)
            for name, role in users:
                user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
                db.add(user)
                db.flush()
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
                ids[name] = str(user.id)
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
        other = Course(name="Pintura")
        db.add_all([course, other])
        db.flush()
        lessons = [Lesson(course_id=course.id, title=f"Aula {n}", order=n) for n in (1, 2)] + [Lesson(course_id=other.id, title="Aula 1", order=1)]
        db.add_all(lessons)
        db.add_all([Enrollment(student_id=ids["ana"], course_id=course.id), Enrollment(student_id=ids["ana"], course_id=other.id)])
        db.flush()
        db.add_all([Progress(student_id=ids["ana"], lesson_id=lesson.id, status=ProgressStatus.done) for lesson in lessons[:2]])
        now = datetime.now(timezone.utc)
        offering = ClassOffering(course_id=course.id, name="Turma Robótica", starts_at=now, ends_at=now + timedelta(days=30),
                                 capacity=20, instructor_id=ids["prof"])
        snack = BenefitItem(name="Lanche", unit="unidade")
        tool = WarehouseItem(name="Kit de tintas", unit="caixa")
        db.add_all([offering, snack, tool])
        db.flush()
        db.add(BenefitDelivery(item_id=snack.id, student_id=ids["ana"], class_offering_id=offering.id, quantity=1, delivered_on=now.date()))
        request = MaterialRequest(requester_id=ids["prof"], class_offering_id=offering.id, purpose="Aula de pintura",
                                  needed_on=now.date(), status=RequestStatus.delivered)
        db.add(request)
        db.flush()
        db.add(MaterialRequestLine(request_id=request.id, item_id=tool.id, quantity_requested=3, quantity_approved=2, quantity_delivered=2))
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
    courses = {course["course_name"]: course for course in dossier.get("courses", [])}
    c.expect(courses.get("Robótica", {}).get("completed") is True and courses["Robótica"]["progress_percent"] == 100, f"completed course: {courses}")
    c.expect(courses.get("Pintura", {}).get("completed") is False, f"course in progress: {courses}")
    benefits = dossier.get("benefits") or []
    c.expect(len(benefits) == 1 and benefits[0]["item_name"] == "Lanche" and benefits[0]["offering_name"] == "Turma Robótica", f"benefits: {benefits}")
    c.expect(len((dossier.get("finance") or {}).get("charges", [])) == 2, "finance statement lists charges")
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
    c.expect([offering["name"] for offering in teacher.get("teaching") or []] == ["Turma Robótica"], f"teacher teaching: {teacher.get('teaching')}")
    materials = teacher.get("materials") or []
    c.expect(len(materials) == 1 and materials[0]["lines"][0]["item_name"] == "Kit de tintas" and materials[0]["lines"][0]["delivered"] == 2,
             f"materials received: {materials}")


async def check_permissions(c: Checker, h: dict, ids: dict) -> None:
    coord = await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 200, "coordinator dossier", h["coord"])
    c.expect(coord.get("guardians") is not None and coord.get("program_enrollments") is not None, "coordinator sees family and academic")
    c.expect(coord.get("finance") is None, f"coordinator has no finance.access: {coord.get('finance')}")
    c.expect(coord.get("materials") is not None, "coordinator sees warehouse reports")
    await c.call("GET", f"/admin/users/{ids['mae']}/dossier", 200, "coordinator can view guardian", h["coord"])

    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 403, "manager outside company", h["gestor"])
    own = await c.call("GET", f"/admin/users/{ids['gestor']}/dossier", 200, "manager own company", h["gestor"])
    c.expect(own.get("organization_name") == "Parceira", f"organization name: {own.get('organization_name')}")
    c.expect(all(own.get(key) is None for key in ("guardians", "finance", "occurrences", "benefits", "materials")), f"manager sections: {own}")

    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 403, "instructor cannot open dossier", h["prof"])
    await c.call("GET", f"/admin/users/{ids['ana']}/dossier", 404, "other institution", h["admin-b"])


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
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
