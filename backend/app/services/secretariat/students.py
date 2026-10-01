from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.repositories.student import StudentRepository


class StudentDirectoryService:
    """Alunos da instituicao ativa, para a secretaria localizar e matricular."""

    def __init__(self, db: Session):
        self.students = StudentRepository(db)

    def list(self) -> list[Student]:
        """Quem tem o papel de aluno aqui, inclusive quem tambem e professor ou funcionario."""
        return self.students.list_with_roles({UserRole.student})
