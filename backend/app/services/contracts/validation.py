from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.signing import verify
from app.models.academic_groups import ProgramEnrollment
from app.models.contracts import ContractStatus
from app.models.student import Student
from app.repositories.contracts import EnrollmentContractRepository
from app.repositories.institution import InstitutionRepository
from app.schemas.contracts import ContractValidationOut
from app.services.contracts.issuing import signature_parts


class ContractValidationService:
    """Validacao publica pelo codigo: existe, foi aceito e o texto nao mudou desde o aceite."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EnrollmentContractRepository(db)
        self.institutions = InstitutionRepository(db)

    def validate(self, code: str) -> ContractValidationOut:
        contract = self.repo.get_by_code_any_institution(code)
        if not contract:
            return ContractValidationOut(valid=False, message="Código não encontrado")
        enrollment = self.db.get(ProgramEnrollment, contract.program_enrollment_id)
        institution = self.institutions.get_by_id(contract.institution_id)
        signer = self.db.get(Student, contract.signer_id) if contract.signer_id else None
        info = {
            "title": contract.title, "student_name": enrollment.student.name if enrollment else None,
            "institution_name": institution.name if institution else None,
            "signer_name": signer.name if signer else None, "signed_at": contract.signed_at,
        }
        if contract.status == ContractStatus.cancelled:
            return ContractValidationOut(valid=False, message="Contrato cancelado", **info)
        if contract.status != ContractStatus.signed:
            return ContractValidationOut(valid=False, message="Contrato ainda não aceito", **info)
        if not verify(contract.signature_hash, signature_parts(contract)):
            return ContractValidationOut(valid=False, message="Assinatura inválida: contrato adulterado", **info)
        return ContractValidationOut(valid=True, message="Contrato aceito e íntegro", **info)
