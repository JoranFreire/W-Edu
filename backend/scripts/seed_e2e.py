"""Popula um banco dedicado com os dados usados pelos testes de navegador (frontend/e2e).

Uso (a partir de backend/, com DATABASE_URL apontando para um banco ja migrado):

    python scripts/seed_e2e.py

Idempotente: se os dados ja existem, nao faz nada. Os testes criam registros com
sufixos unicos, entao o banco pode ser reutilizado entre execucoes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.tenancy import bind_institution
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.institution import Campus, Institution, InstitutionMembership, InstitutionType
from app.models.lesson import Lesson
from app.models.schedule import ClassEnrollment, ClassOffering, ClassStatus
from app.models.student import Student, UserRole

# Mesma senha usada em frontend/e2e/support/users.ts.
PASSWORD = "e2e-senha-123"


def _user(name: str, email: str, role: UserRole, password_hash: str) -> Student:
    return Student(name=name, email=email, password_hash=password_hash, role=role)


def seed() -> None:
    with SessionLocal() as db:
        if db.query(Institution).filter(Institution.slug == "escola-alfa").first():
            print("Dados de e2e ja existem; nada a fazer.")
            return

        password_hash = hash_password(PASSWORD)
        alfa = Institution(slug="escola-alfa", name="Escola Alfa", type=InstitutionType.school)
        beta = Institution(slug="faculdade-beta", name="Faculdade Beta", type=InstitutionType.university)
        db.add_all([alfa, beta])
        db.flush()

        admin = _user("Admin Alfa", "admin@alfa.example.com", UserRole.institution_admin, password_hash)
        aluno = _user("Aluno Alfa", "aluno@alfa.example.com", UserRole.student, password_hash)
        instrutor = _user("Instrutor Alfa", "instrutor@alfa.example.com", UserRole.instructor, password_hash)
        root = _user("Root E2E", "root@e2e.example.com", UserRole.super_admin, password_hash)
        db.add_all([admin, aluno, instrutor, root])
        db.flush()
        memberships = [(alfa, admin), (beta, admin), (alfa, aluno), (alfa, instrutor)]
        db.add_all(InstitutionMembership(institution_id=i.id, user_id=u.id, role=u.role) for i, u in memberships)

        now = datetime.now(timezone.utc)
        bind_institution(db, alfa.id)
        matematica = Course(name="Matemática", description="Curso de matemática")
        historia = Course(name="História", description="Curso de história")
        db.add_all([matematica, historia])
        db.flush()
        db.add_all(Lesson(course_id=matematica.id, title=f"Aula {n}", order=n) for n in (1, 2))
        db.add(Enrollment(student_id=aluno.id, course_id=matematica.id))
        db.add(Campus(name="Campus Centro"))
        turma = ClassOffering(
            course_id=matematica.id,
            name="Turma Matemática",
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=60),
            capacity=30,
            status=ClassStatus.open,
            instructor_id=instrutor.id,
        )
        db.add(turma)
        db.flush()
        db.add(ClassEnrollment(class_offering_id=turma.id, student_id=aluno.id))
        db.commit()

        bind_institution(db, beta.id)
        db.add(Course(name="Direito Civil", description="Curso de direito"))
        db.commit()
    print("Dados de e2e criados.")


if __name__ == "__main__":
    seed()
