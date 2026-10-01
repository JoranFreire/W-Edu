from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.models.social_programs import BenefitVoucher, VoucherStatus
from app.repositories.academic._base import Repository


class BenefitVoucherRepository(Repository[BenefitVoucher]):
    model = BenefitVoucher

    def _with_details(self):
        return self.db.query(BenefitVoucher).options(
            joinedload(BenefitVoucher.item), joinedload(BenefitVoucher.student), joinedload(BenefitVoucher.class_offering),
        )

    def get_by_code(self, code: str, *, lock: bool = False) -> BenefitVoucher | None:
        query = self._with_details().filter(BenefitVoucher.code == code)
        # Trava na validacao: dois leitores com o mesmo QR nao entregam duas vezes.
        return query.with_for_update(of=BenefitVoucher).first() if lock else query.first()

    def list_by_offering(self, offering_id: UUID) -> list[BenefitVoucher]:
        return (
            self._with_details().filter(BenefitVoucher.class_offering_id == offering_id)
            .order_by(BenefitVoucher.released_at.desc(), BenefitVoucher.id.desc()).all()
        )

    def list_by_student(self, student_id: UUID) -> list[BenefitVoucher]:
        return (
            self._with_details().filter(BenefitVoucher.student_id == student_id)
            .order_by(BenefitVoucher.released_at.desc(), BenefitVoucher.id.desc()).all()
        )

    def _pending(self, today: date):
        return self.db.query(BenefitVoucher).filter(
            BenefitVoucher.status == VoucherStatus.released,
            or_(BenefitVoucher.valid_until.is_(None), BenefitVoucher.valid_until >= today),
        )

    def reserved(self, item_ids: list[UUID], today: date) -> dict[UUID, int]:
        """Quantidade liberada e ainda nao retirada (nem vencida): sai do saldo disponivel."""
        if not item_ids:
            return {}
        rows = (
            self._pending(today).with_entities(BenefitVoucher.item_id, func.sum(BenefitVoucher.quantity))
            .filter(BenefitVoucher.item_id.in_(item_ids)).group_by(BenefitVoucher.item_id).all()
        )
        totals = {item_id: int(total or 0) for item_id, total in rows}
        return {item_id: totals.get(item_id, 0) for item_id in item_ids}

    def pending_students(self, offering_id: UUID, item_id: UUID, meeting_id: UUID | None, today: date) -> set[UUID]:
        """Alunos que ja tem este item liberado (e valido) na turma/encontro: nao recebem outro."""
        query = self._pending(today).with_entities(BenefitVoucher.student_id).filter(
            BenefitVoucher.class_offering_id == offering_id, BenefitVoucher.item_id == item_id,
        )
        if meeting_id is not None:
            query = query.filter(BenefitVoucher.scheduled_meeting_id == meeting_id)
        return {row[0] for row in query.all()}
