from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.secretariat import EnrollmentEventKind
from app.schemas.academic_groups import ProgramEnrollmentCreate
from app.services.academic.errors import bad_request
from app.services.academic.program_enrollments import ProgramEnrollmentService
from app.services.secretariat.events import EnrollmentEventRecorder
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class InternalTransferService:
    """Mudanca de programa na instituicao: encerra a matricula atual e abre outra vinculada a ela."""

    def __init__(self, db: Session):
        self.db = db
        self.lifecycle = EnrollmentLifecycleService(db)
        self.enrollments = ProgramEnrollmentService(db)
        self.events = EnrollmentEventRecorder(db)

    def transfer(self, enrollment_id: UUID, program_id: UUID, curriculum_id: UUID | None, reason: str | None, user_id: UUID) -> ProgramEnrollment:
        current = self.lifecycle.get_or_404(enrollment_id)
        if current.program_id == program_id:
            raise bad_request("Escolha um programa diferente do atual")
        details = {"to_program_id": program_id}
        self.lifecycle.transition(enrollment_id, ProgramEnrollmentStatus.transferred, user_id, reason=reason, details=details, commit=False)
        created = self.enrollments.create(
            ProgramEnrollmentCreate(student_id=current.student_id, program_id=program_id, curriculum_id=curriculum_id),
            user_id=user_id,
        )
        created.transferred_from_id = current.id
        self.events.record(created, EnrollmentEventKind.transferred_internal, user_id, reason=reason,
                           details={"from_enrollment_id": current.id, "from_program_id": current.program_id})
        self.db.commit()
        return self.enrollments.get_or_404(created.id)
