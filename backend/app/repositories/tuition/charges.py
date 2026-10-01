from __future__ import annotations

from sqlalchemy import or_

from app.models.finance import Charge
from app.repositories.academic._base import Repository


class TuitionChargeRepository(Repository[Charge]):
    """Cobrancas de mensalidade: por parcela do plano, por matricula e por quem paga."""

    model = Charge

    def existing_installments(self, plan_id: int) -> set[tuple[int, int]]:
        rows = (
            self.db.query(Charge.program_enrollment_id, Charge.installment_number)
            .filter(Charge.tuition_plan_id == plan_id)
            .all()
        )
        return {(enrollment_id, number) for enrollment_id, number in rows}

    def list_by_enrollment(self, enrollment_id: int) -> list[Charge]:
        return (
            self.db.query(Charge)
            .filter(Charge.program_enrollment_id == enrollment_id)
            .order_by(Charge.due_at, Charge.id)
            .all()
        )

    def list_for_user(self, user_id: int) -> list[Charge]:
        """Mensalidades em que o usuario e o aluno ou o responsavel que paga."""
        return (
            self.db.query(Charge)
            .filter(Charge.program_enrollment_id.is_not(None))
            .filter(or_(Charge.student_id == user_id, Charge.payer_id == user_id))
            .order_by(Charge.due_at, Charge.id)
            .all()
        )
