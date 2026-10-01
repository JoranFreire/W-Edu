from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.signing import sign
from app.models.contracts import ContractStatus, EnrollmentContract
from app.models.student import Student
from app.policies.contract_access import ensure_party
from app.repositories.contracts import EnrollmentContractRepository
from app.repositories.guardians import GuardianLinkRepository
from app.schemas.contracts import ContractOut
from app.services.academic.errors import conflict
from app.services.contracts.documents import ContractArchive, contract_pdf
from app.services.contracts.issuing import ContractIssueService, signature_parts, to_out


class ContractPartyService:
    """Lado do aluno e do responsavel financeiro: lista, PDF e aceite eletronico (assinatura de integridade)."""

    def __init__(self, db: Session):
        self.repo = EnrollmentContractRepository(db)
        self.links = GuardianLinkRepository(db)
        self.issuing = ContractIssueService(db)
        self.archive = ContractArchive(db)

    def list_mine(self, user: Student) -> list[ContractOut]:
        return [to_out(contract) for contract in self.repo.list_for_user(user.id)]

    def pdf_for(self, user: Student, contract_id: UUID) -> tuple[EnrollmentContract, bytes]:
        contract = self._as_party(user, contract_id)
        return contract, contract_pdf(contract)

    def accept(self, user: Student, contract_id: UUID) -> ContractOut:
        contract = self._as_party(user, contract_id)
        if contract.status != ContractStatus.pending:
            raise conflict("Contrato não está aguardando aceite")
        contract.status, contract.signer_id = ContractStatus.signed, user.id
        contract.signed_at = datetime.now(timezone.utc).replace(microsecond=0)
        contract.signature_hash = sign(signature_parts(contract))
        self.repo.db.flush()
        self.repo.db.refresh(contract, ["signer"])
        self.archive.archive(contract, user.id, "Aceite eletrônico")
        return to_out(self.repo.save(contract))

    def _as_party(self, user: Student, contract_id: UUID) -> EnrollmentContract:
        contract = self.issuing.get_or_404(contract_id)
        student_id = contract.program_enrollment.student_id
        ensure_party(user, contract, {link.guardian_id for link in self.links.list_by_student(student_id) if link.is_financial})
        return contract
