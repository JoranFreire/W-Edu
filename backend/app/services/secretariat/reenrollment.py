from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollmentStatus
from app.models.secretariat import EnrollmentEventKind, TermRegistration
from app.repositories.secretariat import TermRegistrationRepository
from app.schemas.secretariat import ReenrollInput, TermRegistrationOut
from app.services.academic.errors import bad_request, conflict
from app.services.academic.terms import AcademicTermService
from app.services.secretariat.events import EnrollmentEventRecorder
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class ReenrollmentService:
    """Rematricula: confirma o aluno ativo em um periodo letivo (uma vez por periodo)."""

    def __init__(self, db: Session):
        self.repo = TermRegistrationRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.terms = AcademicTermService(db)
        self.events = EnrollmentEventRecorder(db)

    def list(self, enrollment_id: UUID) -> list[TermRegistrationOut]:
        self.lifecycle.get_or_404(enrollment_id)
        return [self._to_out(registration) for registration in self.repo.list_by_enrollment(enrollment_id)]

    def reenroll(self, enrollment_id: UUID, data: ReenrollInput, user_id: UUID) -> TermRegistrationOut:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        if enrollment.status != ProgramEnrollmentStatus.active:
            raise conflict("Só matrículas ativas podem ser rematriculadas; reative a matrícula antes")
        term = self.terms.get_not_closed(data.term_id)
        duration = enrollment.program.duration_terms
        if data.curriculum_term_number is not None and duration is not None and data.curriculum_term_number > duration:
            raise bad_request("Série/semestre além da duração do programa")
        if self.repo.get(enrollment_id, term.id):
            raise conflict("Aluno já rematriculado neste período")
        registration = self.repo.add(TermRegistration(
            program_enrollment_id=enrollment_id, term_id=term.id,
            curriculum_term_number=data.curriculum_term_number, created_by_id=user_id,
        ))
        self.events.record(enrollment, EnrollmentEventKind.reenrolled, user_id, term_id=term.id,
                           details={"curriculum_term_number": data.curriculum_term_number})
        self.repo.commit()
        return self._to_out(registration)

    @staticmethod
    def _to_out(registration: TermRegistration) -> TermRegistrationOut:
        return TermRegistrationOut(
            id=registration.id,
            term_id=registration.term_id,
            term_name=registration.term.name,
            curriculum_term_number=registration.curriculum_term_number,
            registered_at=registration.registered_at,
        )
