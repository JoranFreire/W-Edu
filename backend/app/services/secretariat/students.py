from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.services.student import StudentService


class StudentDirectoryService:
    """Alunos da instituicao ativa, para a secretaria localizar e matricular."""

    def __init__(self, db: Session):
        self.students = StudentService(db)

    def list(self) -> list[Student]:
        return [user for user in self.students.list_all() if user.role == UserRole.student]
