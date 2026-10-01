from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.completion import Internship, InternshipLog, InternshipStatus, ReviewStatus
from app.models.student import Student
from app.policies.completion_access import ensure_can_supervise, ensure_can_view_internship, ensure_own
from app.repositories.completion import InternshipLogRepository
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.completion.internships import InternshipService
from app.schemas.completion import InternshipLogCreate


class InternshipLogService:
    """Diario de estagio supervisionado: o aluno lanca as horas, o orientador ou a coordenacao valida."""

    def __init__(self, db: Session):
        self.repo = InternshipLogRepository(db)
        self.internships = InternshipService(db)

    def list(self, internship_id: UUID, user: Student) -> list[InternshipLog]:
        internship = self.internships.get_or_404(internship_id)
        ensure_can_view_internship(user, internship.program_enrollment.student_id, internship.advisor_id)
        return self.repo.list_by_internship(internship_id)

    def add(self, student: Student, internship_id: UUID, data: InternshipLogCreate) -> InternshipLog:
        internship = self._own_internship(student, internship_id)
        if internship.status != InternshipStatus.in_progress:
            raise conflict("O estágio não está em andamento")
        if data.worked_on < internship.starts_on or (internship.ends_on and data.worked_on > internship.ends_on):
            raise bad_request("A data está fora do período do estágio")
        return self.repo.save(InternshipLog(internship_id=internship.id, **data.model_dump()))

    def remove(self, student: Student, log_id: UUID) -> None:
        log = self._get_or_404(log_id)
        self._own_internship(student, log.internship_id)
        if log.status != ReviewStatus.submitted:
            raise conflict("Registro já validado")
        self.repo.delete(log)

    def review(self, log_id: UUID, approved: bool, reviewer: Student) -> InternshipLog:
        log = self._get_or_404(log_id)
        ensure_can_supervise(reviewer, log.internship.advisor_id)
        if log.status != ReviewStatus.submitted:
            raise conflict("Registro já validado")
        log.status = ReviewStatus.approved if approved else ReviewStatus.rejected
        log.reviewed_by_id, log.reviewed_at = reviewer.id, datetime.now(timezone.utc)
        return self.repo.save(log)

    def _own_internship(self, student: Student, internship_id: UUID) -> Internship:
        internship = self.internships.get_or_404(internship_id)
        ensure_own(internship.program_enrollment, student)
        return internship

    def _get_or_404(self, log_id: UUID) -> InternshipLog:
        log = self.repo.get_by_id(log_id)
        if not log:
            raise not_found("Registro de horas não encontrado")
        return log
