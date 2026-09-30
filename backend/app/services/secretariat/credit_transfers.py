from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollmentStatus
from app.models.secretariat import CreditTransfer, CreditTransferStatus
from app.repositories.secretariat import CreditTransferRepository
from app.schemas.secretariat import CreditTransferCreate, CreditTransferDecision, CreditTransferOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.secretariat.lifecycle import EnrollmentLifecycleService

OPEN = (ProgramEnrollmentStatus.active, ProgramEnrollmentStatus.locked)


class CreditTransferService:
    """Aproveitamento de estudos: a secretaria registra, a coordenacao decide."""

    def __init__(self, db: Session):
        self.repo = CreditTransferRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def list(self, enrollment_id: int) -> list[CreditTransferOut]:
        self.lifecycle.get_or_404(enrollment_id)
        return [self._to_out(transfer) for transfer in self.repo.list_by_enrollment(enrollment_id)]

    def request(self, enrollment_id: int, data: CreditTransferCreate) -> CreditTransferOut:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        if enrollment.status not in OPEN:
            raise conflict("Matrícula encerrada não recebe aproveitamento")
        if data.subject_id not in {component.subject_id for component in enrollment.curriculum.components}:
            raise bad_request("A disciplina não faz parte da matriz do aluno")
        if self.repo.active_for_subject(enrollment_id, data.subject_id):
            raise conflict("Já existe aproveitamento pendente ou aprovado para esta disciplina")
        return self._to_out(self.repo.save(CreditTransfer(program_enrollment_id=enrollment_id, **data.model_dump())))

    def decide(self, transfer_id: int, data: CreditTransferDecision, user_id: int) -> CreditTransferOut:
        transfer = self.repo.get_by_id(transfer_id)
        if not transfer:
            raise not_found("Aproveitamento não encontrado")
        if transfer.status != CreditTransferStatus.requested:
            raise conflict("Aproveitamento já decidido")
        transfer.status = CreditTransferStatus.approved if data.approved else CreditTransferStatus.rejected
        transfer.decision_note, transfer.decided_by_id, transfer.decided_at = data.note, user_id, datetime.now(timezone.utc)
        return self._to_out(self.repo.save(transfer))

    @staticmethod
    def _to_out(transfer: CreditTransfer) -> CreditTransferOut:
        return CreditTransferOut(
            id=transfer.id, subject_id=transfer.subject_id, subject_code=transfer.subject.code, subject_name=transfer.subject.name,
            origin=transfer.origin, source_institution=transfer.source_institution, source_subject=transfer.source_subject,
            grade=transfer.grade, hours=transfer.hours, status=transfer.status, decision_note=transfer.decision_note,
            decided_at=transfer.decided_at, created_at=transfer.created_at,
        )
