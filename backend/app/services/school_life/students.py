from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.tenancy import bound_institution_id
from app.models.student import Student, UserRole
from app.repositories.student import StudentRepository
from app.services.academic.errors import not_found
from app.services.membership import MembershipService


class SchoolStudentLookup:
    """Localiza um aluno que seja membro da instituicao da requisicao."""

    def __init__(self, db: Session):
        self.db = db
        self.users = StudentRepository(db)
        self.memberships = MembershipService(db)

    def get_or_404(self, student_id: UUID) -> Student:
        student = self.users.get_by_id(student_id)
        if not student or student.role != UserRole.student or not self.memberships.get(bound_institution_id(self.db), student.id):
            raise not_found("Aluno não encontrado")
        return student
