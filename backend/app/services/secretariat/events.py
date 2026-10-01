from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.secretariat import EnrollmentEventKind, ProgramEnrollmentEvent
from app.repositories.secretariat import EnrollmentEventRepository


class EnrollmentEventRecorder:
    """Registra movimentacoes da matricula (sem commit; quem chama fecha a transacao)."""

    def __init__(self, db: Session):
        self.repo = EnrollmentEventRepository(db)

    def record(
        self,
        enrollment: ProgramEnrollment,
        kind: EnrollmentEventKind,
        user_id: UUID | None,
        *,
        reason: str | None = None,
        term_id: UUID | None = None,
        details: dict | None = None,
    ) -> ProgramEnrollmentEvent:
        return self.repo.add(ProgramEnrollmentEvent(
            program_enrollment_id=enrollment.id,
            kind=kind,
            term_id=term_id,
            reason=reason,
            details=details or {},
            created_by_id=user_id,
        ))

    def list(self, enrollment_id: UUID) -> list[ProgramEnrollmentEvent]:
        return self.repo.list_by_enrollment(enrollment_id)
