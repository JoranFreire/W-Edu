"""Exercise the certification flow end to end through real requests.

Eligibility, manual issue, signature, PDF download, public validation,
revocation, reissue and automatic issue. Uses a temporary SQLite database by
default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_certificate_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ.setdefault("CERTIFICATES_STORAGE_DIR", tempfile.mkdtemp(prefix="wedu_certificates_"))

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
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.institution import Institution, InstitutionMembership
from app.models.lesson import Lesson
from app.models.progress import Progress, ProgressStatus
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


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola")
        db.add(institution)
        db.flush()
        bind_institution(db, institution.id)
        admin = Student(name="Admin", email="admin@example.com", password_hash=hash_password(PASSWORD), role=UserRole.admin)
        aluno = Student(name="Aluno", email="aluno@example.com", password_hash=hash_password(PASSWORD), role=UserRole.student)
        db.add_all([admin, aluno])
        db.flush()
        db.add_all(InstitutionMembership(institution_id=institution.id, user_id=u.id, role=u.role) for u in (admin, aluno))
        course = Course(name="Curso Online")
        auto_course = Course(name="Curso Automatico")
        db.add_all([course, auto_course])
        db.flush()
        lessons = [Lesson(course_id=course.id, title=f"Aula {n}", order=n) for n in (1, 2)]
        auto_lesson = Lesson(course_id=auto_course.id, title="Unica", order=1)
        db.add_all([*lessons, auto_lesson])
        db.add_all([Enrollment(student_id=aluno.id, course_id=course.id), Enrollment(student_id=aluno.id, course_id=auto_course.id)])
        db.commit()
        return {
            "aluno": aluno.id, "course": course.id, "lesson1": lessons[0].id, "lesson2": lessons[1].id,
            "auto_course": auto_course.id, "auto_lesson": auto_lesson.id, "institution": institution.id,
        }


def complete_lesson(ids: dict[str, int], lesson_key: str) -> None:
    with SessionLocal() as db:
        bind_institution(db, ids["institution"])
        db.add(Progress(student_id=ids["aluno"], lesson_id=ids[lesson_key], status=ProgressStatus.done))
        db.commit()


async def run() -> int:
    ids = seed()
    failures: list[str] = []

    def expect(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        async def login(email: str) -> dict[str, str]:
            response = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
            return {"Authorization": f"Bearer {response.json()['access_token']}"}

        admin = await login("admin@example.com")
        aluno = await login("aluno@example.com")
        course, student = ids["course"], ids["aluno"]

        r = await client.get(f"/certificates/rules/{course}", headers=admin)
        expect(r.status_code == 200 and r.json()["require_attendance"] is False, f"default rule for online course: {r.text}")
        r = await client.patch(f"/certificates/rules/{course}", json={"auto_issue": False}, headers=admin)
        expect(r.status_code == 200 and r.json()["auto_issue"] is False, f"update rule: {r.text}")

        complete_lesson(ids, "lesson1")
        r = await client.get(f"/certificates/courses/{course}/students/{student}/eligibility", headers=admin)
        body = r.json()
        expect(body["eligible"] is False and body["progress_percent"] == 50, f"half progress not eligible: {body}")
        r = await client.post(f"/certificates/courses/{course}/students/{student}/issue", headers=admin)
        expect(r.status_code == 400, f"issue blocked while ineligible: {r.status_code}")

        complete_lesson(ids, "lesson2")
        r = await client.post(f"/certificates/courses/{course}/students/{student}/issue", headers=admin)
        expect(r.status_code == 200, f"issue when eligible: {r.status_code} {r.text}")
        certificate_id, code = r.json()["certificate_id"], r.json()["validation_code"]

        r = await client.get(f"/certificates/validate/{code}")
        expect(r.json()["valid"] is True and r.json()["signature_valid"] is True, f"public validation: {r.text}")
        r = await client.get(f"/certificates/{certificate_id}/download", headers=aluno)
        expect(r.status_code == 200 and r.content.startswith(b"%PDF-1.4"), f"owner downloads PDF: {r.status_code}")

        r = await client.post(f"/certificates/{certificate_id}/revoke", json={"reason": "teste"}, headers=admin)
        expect(r.status_code == 200 and r.json()["revoked_at"], f"revoke: {r.text}")
        r = await client.get(f"/certificates/validate/{code}")
        expect(r.json()["valid"] is False and r.json()["message"] == "Certificado revogado", f"revoked validation: {r.text}")
        r = await client.get(f"/certificates/{certificate_id}/download", headers=aluno)
        expect(r.status_code == 400, f"revoked download blocked: {r.status_code}")

        r = await client.post(f"/certificates/courses/{course}/students/{student}/issue", headers=admin)
        expect(r.status_code == 200 and r.json()["validation_code"] != code, f"reissue gets new code: {r.text}")

        # Emissao automatica: consumir a aula nao basta (fica em andamento); depois de concluida,
        # consumir de novo nao pode rebaixar o progresso e dispara a emissao.
        r = await client.post(f"/progress/consume/{ids['auto_lesson']}", headers=aluno)
        expect(r.status_code == 200, f"consume lesson: {r.status_code}")
        r = await client.get("/certificates/students/me", headers=aluno)
        expect(len(r.json()) == 1, f"no auto certificate while in progress: {r.json()}")
        mark_auto_lesson_done(ids)
        r = await client.post(f"/progress/consume/{ids['auto_lesson']}", headers=aluno)
        r = await client.get("/certificates/students/me", headers=aluno)
        expect(len(r.json()) == 2, f"auto certificate after completion: {r.json()}")

    if failures:
        print("Certificate flow check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Certificate flow check passed.")
    return 0


def mark_auto_lesson_done(ids: dict[str, int]) -> None:
    with SessionLocal() as db:
        bind_institution(db, ids["institution"])
        progress = db.query(Progress).filter(Progress.student_id == ids["aluno"], Progress.lesson_id == ids["auto_lesson"]).one()
        progress.status = ProgressStatus.done
        db.commit()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
