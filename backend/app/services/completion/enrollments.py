from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.student import Student
from app.policies.completion_access import ensure_own
from app.repositories.academic import ProgramEnrollmentRepository


class OwnEnrollmentLookup:
    """Matricula no programa que pertence ao aluno autenticado."""

    def __init__(self, db: Session):
        self.repo = ProgramEnrollmentRepository(db)

    def get(self, student: Student, enrollment_id: UUID) -> ProgramEnrollment:
        return ensure_own(self.repo.get_by_id(enrollment_id), student)
