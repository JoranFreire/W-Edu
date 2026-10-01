"""Quem le e quem aceita o contrato: o aluno ou o responsavel financeiro dele; a secretaria so le."""

from fastapi import HTTPException, status

from app.models.contracts import EnrollmentContract
from app.models.student import ADMIN_ROLES, Student, UserRole

OFFICE = ADMIN_ROLES | {UserRole.coordinator, UserRole.secretary}


def ensure_party(user: Student, contract: EnrollmentContract, financial_guardian_ids: set[int]) -> None:
    """Parte do contrato: o proprio aluno ou o responsavel financeiro (os demais recebem 404)."""
    if user.id == contract.program_enrollment.student_id or user.id in financial_guardian_ids:
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")
