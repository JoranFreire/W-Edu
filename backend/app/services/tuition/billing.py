from __future__ import annotations

from datetime import datetime, time, timezone

from sqlalchemy.orm import Session

from app.models.finance import Charge
from app.models.tuition import TuitionPlan
from app.repositories.tuition import StudentDiscountRepository, TuitionChargeRepository
from app.schemas.tuition import GenerationOut
from app.services.academic.errors import conflict
from app.services.tuition.payer import PayerResolver
from app.services.tuition.plans import TuitionPlanService
from app.services.tuition.rules import Discount, compose, due_dates, installment_gross
from app.services.tuition.targets import BillingTarget, BillingTargets


class TuitionBillingService:
    """Gera as parcelas do plano para cada matricula alvo; rodar de novo so cria as que faltam."""

    def __init__(self, db: Session):
        self.db = db
        self.plans = TuitionPlanService(db)
        self.targets = BillingTargets(db)
        self.charges = TuitionChargeRepository(db)
        self.discounts = StudentDiscountRepository(db)
        self.payers = PayerResolver(db)

    def generate(self, plan_id: int) -> GenerationOut:
        plan = self.plans.get_or_404(plan_id)
        if not plan.is_active:
            raise conflict("Plano inativo")
        existing = self.charges.existing_installments(plan.id)
        targets = self.targets.for_plan(plan)
        created = skipped = 0
        for target in targets:
            for number, due_on in enumerate(due_dates(plan.first_due_on, plan.installments), start=1):
                if (target.enrollment.id, number) in existing:
                    skipped += 1
                    continue
                self.db.add(self._charge(plan, target, number, due_on))
                created += 1
        self.db.commit()
        return GenerationOut(enrollments=len(targets), created=created, skipped=skipped)

    def _charge(self, plan: TuitionPlan, target: BillingTarget, number: int, due_on) -> Charge:
        enrollment = target.enrollment
        discounts = [Discount(d.kind, d.percent, d.amount_cents) for d in self.discounts.active_on(enrollment.id, due_on)]
        composition = compose(installment_gross(plan.amount_cents, plan.installments, target.credits), discounts)
        return Charge(
            student_id=enrollment.student_id, payer_id=self.payers.payer_of(enrollment.student_id),
            program_enrollment_id=enrollment.id, tuition_plan_id=plan.id, installment_number=number,
            gross_amount_cents=composition.gross, discount_cents=composition.discount,
            punctuality_discount_cents=composition.punctuality, amount_cents=composition.amount,
            due_at=datetime.combine(due_on, time(12), tzinfo=timezone.utc),
            description=f"{plan.name} — parcela {number}/{plan.installments}",
        )
