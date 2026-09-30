"""Popula um banco dedicado com instituicoes, usuarios e conteudo para o teste de carga.

Uso (a partir de backend/, com DATABASE_URL apontando para um banco de teste
ja migrado com `alembic upgrade head`):

    python loadtest/seed.py --institutions 5 --students 200 --courses 5 --lessons 10

Gera loadtest/seed.json, lido pelo locustfile.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.tenancy import bind_institution
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.institution import Institution, InstitutionMembership, InstitutionType
from app.models.lesson import Lesson
from app.models.schedule import CheckinToken, ClassEnrollment, ClassOffering, ClassStatus, ScheduledMeeting
from app.models.student import Student, UserRole

PASSWORD = "loadtest123"
SLUG_PREFIX = "lt-"
SEED_FILE = Path(__file__).with_name("seed.json")
TYPES = [InstitutionType.school, InstitutionType.university, InstitutionType.vocational]


def seed(institutions: int, students: int, courses: int, lessons: int) -> dict:
    password_hash = hash_password(PASSWORD)  # bcrypt e lento: um hash para todos
    now = datetime.now(timezone.utc)
    output = {"password": PASSWORD, "institutions": []}

    with SessionLocal() as db:
        if db.query(Institution).filter(Institution.slug.like(f"{SLUG_PREFIX}%")).first():
            raise SystemExit("Ja existem instituicoes de carga (lt-*). Use um banco novo para o teste.")

        for i in range(1, institutions + 1):
            slug = f"{SLUG_PREFIX}{i}"
            institution = Institution(slug=slug, name=f"Instituicao Carga {i}", type=TYPES[(i - 1) % len(TYPES)])
            db.add(institution)
            db.flush()
            bind_institution(db, institution.id)

            admin = Student(name=f"Admin {slug}", email=f"admin.{slug}@example.com", password_hash=password_hash, role=UserRole.institution_admin)
            student_rows = [
                Student(name=f"Aluno {j} {slug}", email=f"aluno{j}.{slug}@example.com", password_hash=password_hash, role=UserRole.student)
                for j in range(1, students + 1)
            ]
            db.add(admin)
            db.add_all(student_rows)
            db.flush()
            db.add_all(
                InstitutionMembership(institution_id=institution.id, user_id=user.id, role=user.role)
                for user in [admin, *student_rows]
            )

            course_rows = [Course(name=f"Curso {c} {slug}", description="Curso de carga") for c in range(1, courses + 1)]
            db.add_all(course_rows)
            db.flush()
            lesson_rows = [
                Lesson(course_id=course.id, title=f"Aula {n}", content="Conteudo " * 50, order=n)
                for course in course_rows
                for n in range(1, lessons + 1)
            ]
            db.add_all(lesson_rows)
            db.add_all(Enrollment(student_id=s.id, course_id=course.id) for s in student_rows for course in course_rows)

            class_offering = ClassOffering(
                course_id=course_rows[0].id,
                name=f"Turma carga {slug}",
                starts_at=now - timedelta(days=1),
                ends_at=now + timedelta(days=90),
                capacity=students + 10,
                status=ClassStatus.open,
            )
            db.add(class_offering)
            db.flush()
            db.add_all(ClassEnrollment(class_offering_id=class_offering.id, student_id=s.id) for s in student_rows)
            meeting = ScheduledMeeting(
                class_offering_id=class_offering.id,
                title="Encontro de carga",
                starts_at=now - timedelta(minutes=5),
                ends_at=now + timedelta(hours=12),
            )
            db.add(meeting)
            db.flush()
            token = CheckinToken(scheduled_meeting_id=meeting.id, token=secrets.token_urlsafe(24), expires_at=now + timedelta(days=2))
            db.add(token)
            db.commit()

            output["institutions"].append(
                {
                    "slug": slug,
                    "admin": admin.email,
                    "students": [s.email for s in student_rows],
                    "courses": [course.id for course in course_rows],
                    "lessons": {str(course.id): [l.id for l in lesson_rows if l.course_id == course.id] for course in course_rows},
                    "class_id": class_offering.id,
                    "meeting_id": meeting.id,
                    "checkin_token": token.token,
                }
            )
            print(f"{slug}: {students} alunos, {courses} cursos, {courses * lessons} aulas")

    SEED_FILE.write_text(json.dumps(output, indent=2))
    print(f"Seed salvo em {SEED_FILE}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--institutions", type=int, default=5)
    parser.add_argument("--students", type=int, default=200)
    parser.add_argument("--courses", type=int, default=5)
    parser.add_argument("--lessons", type=int, default=10)
    args = parser.parse_args()
    seed(args.institutions, args.students, args.courses, args.lessons)
