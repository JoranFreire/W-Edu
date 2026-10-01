from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student
from app.policies.completion_access import ADVISOR_ROLES
from app.repositories.student import StudentRepository


class AdvisorDirectory:
    """Docentes e coordenadores da instituicao que podem orientar estagio e TCC."""

    def __init__(self, db: Session):
        self.users = StudentRepository(db)

    def list(self) -> list[Student]:
        return self.users.list_active_by_roles(ADVISOR_ROLES)
