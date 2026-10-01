from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.repositories.completion import FinalProjectRepository, InternshipRepository
from app.schemas.completion import AdvisingOut
from app.services.completion.final_projects import to_out
from app.services.completion.internships import InternshipService


class AdvisingService:
    """Orientacoes em andamento: as do instrutor ou, para a coordenacao, todas."""

    def __init__(self, db: Session):
        self.internships = InternshipRepository(db)
        self.internship_view = InternshipService(db)
        self.final_projects = FinalProjectRepository(db)

    def for_user(self, user: Student) -> AdvisingOut:
        advisor_id = user.id if user.role == UserRole.instructor else None
        return AdvisingOut(
            internships=self.internship_view.to_out(self.internships.list_supervised(advisor_id)),
            final_projects=[to_out(project) for project in self.final_projects.list_supervised(advisor_id)],
        )
