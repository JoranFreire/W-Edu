from __future__ import annotations
from uuid import UUID

from app.models.academic_groups import ProgramEnrollment
from app.models.completion import FinalProject, FinalProjectStatus
from app.repositories.academic._base import Repository

OPEN = (FinalProjectStatus.in_progress, FinalProjectStatus.submitted)


class FinalProjectRepository(Repository[FinalProject]):
    model = FinalProject

    def get_by_enrollment(self, enrollment_id: UUID) -> FinalProject | None:
        return self.db.query(FinalProject).filter(FinalProject.program_enrollment_id == enrollment_id).first()

    def list_by_student(self, student_id: UUID) -> list[FinalProject]:
        return (
            self.db.query(FinalProject)
            .join(ProgramEnrollment, ProgramEnrollment.id == FinalProject.program_enrollment_id)
            .filter(ProgramEnrollment.student_id == student_id)
            .order_by(FinalProject.id)
            .all()
        )

    def list_supervised(self, advisor_id: UUID | None) -> list[FinalProject]:
        """TCCs em andamento do orientador (sem orientador informado: todos, para a coordenacao)."""
        query = self.db.query(FinalProject).filter(FinalProject.status.in_(OPEN))
        if advisor_id is not None:
            query = query.filter(FinalProject.advisor_id == advisor_id)
        return query.order_by(FinalProject.id).all()
