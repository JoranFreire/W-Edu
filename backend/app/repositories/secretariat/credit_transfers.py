from __future__ import annotations
from uuid import UUID

from app.models.secretariat import CreditTransfer, CreditTransferStatus
from app.repositories.academic._base import Repository


class CreditTransferRepository(Repository[CreditTransfer]):
    model = CreditTransfer

    def list_by_enrollment(self, enrollment_id: UUID) -> list[CreditTransfer]:
        return (
            self.db.query(CreditTransfer)
            .filter(CreditTransfer.program_enrollment_id == enrollment_id)
            .order_by(CreditTransfer.created_at)
            .all()
        )

    def active_for_subject(self, enrollment_id: UUID, subject_id: UUID) -> CreditTransfer | None:
        """Pedido pendente ou aprovado para a disciplina (rejeitados podem ser refeitos)."""
        return (
            self.db.query(CreditTransfer)
            .filter(
                CreditTransfer.program_enrollment_id == enrollment_id,
                CreditTransfer.subject_id == subject_id,
                CreditTransfer.status != CreditTransferStatus.rejected,
            )
            .first()
        )

    def approved(self, enrollment_id: UUID) -> list[CreditTransfer]:
        return (
            self.db.query(CreditTransfer)
            .filter(CreditTransfer.program_enrollment_id == enrollment_id, CreditTransfer.status == CreditTransferStatus.approved)
            .all()
        )
