from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.academic import CurriculumStatus
from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus as Status
from app.models.secretariat import EnrollmentEventKind as Kind
from app.repositories.academic import CurriculumRepository, ProgramEnrollmentRepository
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.transitions import can_change_enrollment
from app.services.secretariat.events import EnrollmentEventRecorder

EVENT_FOR_STATUS = {
    Status.active: Kind.reactivated,
    Status.locked: Kind.locked,
    Status.cancelled: Kind.cancelled,
    Status.dropped: Kind.dropped,
    Status.transferred: Kind.transferred_out,
    Status.graduated: Kind.graduated,
}


class EnrollmentLifecycleService:
    """Trancamento, reativacao, cancelamento, evasao, transferencia externa e troca de matriz."""

    def __init__(self, db: Session):
        self.repo = ProgramEnrollmentRepository(db)
        self.curricula = CurriculumRepository(db)
        self.events = EnrollmentEventRecorder(db)

    def get_or_404(self, enrollment_id: UUID) -> ProgramEnrollment:
        enrollment = self.repo.get_by_id(enrollment_id)
        if not enrollment:
            raise not_found("Matrícula não encontrada")
        return enrollment

    def transition(
        self,
        enrollment_id: UUID,
        target: Status,
        user_id: UUID | None,
        *,
        reason: str | None = None,
        details: dict | None = None,
        commit: bool = True,
    ) -> ProgramEnrollment:
        enrollment = self.get_or_404(enrollment_id)
        if not can_change_enrollment(enrollment.status, target):
            raise conflict(f"Transição de {enrollment.status.value} para {target.value} não permitida")
        if target == Status.active and self.repo.get_open(enrollment.student_id, enrollment.program_id) not in (None, enrollment):
            raise conflict("Aluno já possui outra matrícula aberta neste programa")
        enrollment.status = target
        enrollment.status_changed_at = datetime.now(timezone.utc)
        self.events.record(enrollment, EVENT_FOR_STATUS[target], user_id, reason=reason, details=details)
        return self.repo.save(enrollment) if commit else enrollment

    def transfer_out(self, enrollment_id: UUID, destination: str, reason: str | None, user_id: UUID) -> ProgramEnrollment:
        return self.transition(enrollment_id, Status.transferred, user_id, reason=reason, details={"destination": destination})

    def change_curriculum(self, enrollment_id: UUID, curriculum_id: UUID, reason: str | None, user_id: UUID) -> ProgramEnrollment:
        """Migracao de matriz: o aluno passa a seguir outra versao do mesmo programa."""
        enrollment = self.get_or_404(enrollment_id)
        if enrollment.status not in (Status.active, Status.locked):
            raise conflict("Só matrículas ativas ou trancadas mudam de matriz")
        curriculum = self.curricula.get_by_id(curriculum_id)
        if not curriculum or curriculum.program_id != enrollment.program_id:
            raise not_found("Matriz curricular não encontrada neste programa")
        if curriculum.status == CurriculumStatus.draft:
            raise bad_request("Matriz em rascunho não recebe alunos")
        if curriculum.id == enrollment.curriculum_id:
            raise conflict("O aluno já segue esta matriz")
        previous = enrollment.curriculum_id
        enrollment.curriculum_id = curriculum.id
        self.events.record(enrollment, Kind.curriculum_changed, user_id, reason=reason,
                           details={"from_curriculum_id": previous, "to_curriculum_id": curriculum.id})
        return self.repo.save(enrollment)
