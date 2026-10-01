from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.finance import Charge
from app.models.student import Student
from app.policies.tuition_access import ensure_can_view_charge
from app.repositories.tuition import TuitionChargeRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.tuition import SettlementOut, TuitionChargeOut
from app.services.secretariat.lifecycle import EnrollmentLifecycleService
from app.services.tuition.late_fees import LateFeeSettingsService
from app.services.tuition.settlement import OPEN, TuitionSettlementService, due_on, quote


class TuitionStatementService:
    """Extrato de mensalidades: da matricula (financeiro) ou do usuario como aluno ou pagador."""

    def __init__(self, db: Session):
        self.repo = TuitionChargeRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.late_fees = LateFeeSettingsService(db)
        self.settlement = TuitionSettlementService(db)

    def for_enrollment(self, enrollment_id: int) -> list[TuitionChargeOut]:
        self.lifecycle.get_or_404(enrollment_id)
        return self._out(self.repo.list_by_enrollment(enrollment_id))

    def for_user(self, user: Student) -> list[TuitionChargeOut]:
        return self._out(self.repo.list_for_user(user.id))

    def quote_for(self, user: Student, charge_id: int, on: date | None) -> SettlementOut:
        charge = self.settlement.get_or_404(charge_id)
        ensure_can_view_charge(user, charge)
        return quote(charge, on or date.today(), self.late_fees.policy())

    def _out(self, charges: list[Charge]) -> list[TuitionChargeOut]:
        policy, today = self.late_fees.policy(), date.today()
        return [
            TuitionChargeOut(
                id=c.id, student=PersonSummary.model_validate(c.student) if c.student else None,
                payer=PersonSummary.model_validate(c.payer) if c.payer else None,
                program_enrollment_id=c.program_enrollment_id, tuition_plan_id=c.tuition_plan_id,
                installment_number=c.installment_number, description=c.description, due_on=due_on(c), status=c.status,
                gross_amount_cents=c.gross_amount_cents, discount_cents=c.discount_cents,
                punctuality_discount_cents=c.punctuality_discount_cents, amount_cents=c.amount_cents,
                fine_cents=c.fine_cents, interest_cents=c.interest_cents, amount_paid_cents=c.amount_paid_cents, paid_at=c.paid_at,
                quote=quote(c, today, policy) if c.status in OPEN else None,
            )
            for c in charges
        ]
