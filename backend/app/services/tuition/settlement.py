from __future__ import annotations
from uuid import UUID

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.finance import Charge, ChargeStatus, PaymentMethod
from app.repositories.tuition import TuitionChargeRepository
from app.schemas.tuition import SettlementOut
from app.services.academic.errors import conflict, not_found
from app.services.tuition.late_fees import LateFeeSettingsService
from app.services.tuition.rules import LateFeePolicy, settle

OPEN = (ChargeStatus.pending, ChargeStatus.failed)


def due_on(charge: Charge) -> date | None:
    """Vencimento gravado ao meio-dia UTC; a data e a do proprio dia."""
    return charge.due_at.date() if charge.due_at else None


def quote(charge: Charge, on: date, policy: LateFeePolicy) -> SettlementOut:
    due = due_on(charge) or on
    result = settle(charge.amount_cents, charge.punctuality_discount_cents, due, on, policy)
    return SettlementOut(
        on=on, base_cents=result.base, punctuality_discount_cents=result.punctuality,
        fine_cents=result.fine, interest_cents=result.interest, total_cents=result.total,
    )


class TuitionSettlementService:
    """Valor a pagar numa data (pontualidade ou multa e juros) e baixa da parcela."""

    def __init__(self, db: Session):
        self.repo = TuitionChargeRepository(db)
        self.late_fees = LateFeeSettingsService(db)

    def quote(self, charge_id: UUID, on: date | None = None) -> SettlementOut:
        charge = self.get_or_404(charge_id)
        return quote(charge, on or date.today(), self.late_fees.policy())

    def settle(self, charge_id: UUID, paid_on: date | None, method: PaymentMethod) -> Charge:
        charge = self.get_or_404(charge_id)
        if charge.status not in OPEN:
            raise conflict("Cobrança já quitada ou cancelada")
        result = quote(charge, paid_on or date.today(), self.late_fees.policy())
        charge.fine_cents, charge.interest_cents = result.fine_cents, result.interest_cents
        charge.amount_paid_cents = result.total_cents
        charge.status, charge.payment_method, charge.paid_at = ChargeStatus.paid, method, datetime.now(timezone.utc)
        return self.repo.save(charge)

    def get_or_404(self, charge_id: UUID) -> Charge:
        charge = self.repo.get_by_id(charge_id)
        if not charge:
            raise not_found("Cobrança não encontrada")
        return charge
