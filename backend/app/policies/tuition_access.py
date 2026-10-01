"""Quem ve uma cobranca de mensalidade: financeiro, o aluno ou o responsavel que paga."""

from fastapi import HTTPException, status

from app.models.finance import Charge
from app.models.student import ADMIN_ROLES, Student, UserRole

FINANCE_STAFF = ADMIN_ROLES | {UserRole.secretary}


def ensure_can_view_charge(user: Student, charge: Charge) -> None:
    if user.role in FINANCE_STAFF or user.id in (charge.student_id, charge.payer_id):
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cobrança não encontrada")
