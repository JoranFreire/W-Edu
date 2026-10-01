from __future__ import annotations
from uuid import UUID

import hashlib

from sqlalchemy.orm import Session

from app.core.signing import timestamp, validation_code
from app.models.contracts import ContractStatus, EnrollmentContract
from app.repositories.contracts import EnrollmentContractRepository
from app.schemas.contracts import ContractIssue, ContractOut
from app.services.academic.errors import conflict, not_found
from app.services.academic.terms import AcademicTermService
from app.services.contracts.documents import ContractArchive
from app.services.contracts.fields import ContractFields
from app.services.contracts.templates import ContractTemplateService
from app.services.notifications.templates import render_template
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


def signature_parts(contract: EnrollmentContract) -> list[str]:
    """O que o aceite assina: codigo, texto congelado, quem aceitou e quando."""
    body_hash = hashlib.sha256(contract.body.encode("utf-8")).hexdigest()
    return [contract.validation_code, body_hash, str(contract.signer_id), timestamp(contract.signed_at) if contract.signed_at else ""]


def to_out(contract: EnrollmentContract) -> ContractOut:
    enrollment = contract.program_enrollment
    return ContractOut(
        id=contract.id, program_enrollment_id=enrollment.id, student_name=enrollment.student.name,
        registration_number=enrollment.registration_number, kind=contract.kind, title=contract.title, body=contract.body,
        status=contract.status, validation_code=contract.validation_code,
        signer_name=contract.signer.name if contract.signer else None, signed_at=contract.signed_at,
        document_id=contract.document_id, created_at=contract.created_at,
    )


class ContractIssueService:
    """Emissao (texto do modelo com os dados da matricula), consulta e cancelamento pela secretaria."""

    def __init__(self, db: Session):
        self.repo = EnrollmentContractRepository(db)
        self.templates = ContractTemplateService(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.terms = AcademicTermService(db)
        self.fields = ContractFields(db)
        self.archive = ContractArchive(db)

    def list(self, enrollment_id: UUID) -> list[ContractOut]:
        self.lifecycle.get_or_404(enrollment_id)
        return [to_out(contract) for contract in self.repo.list_by_enrollment(enrollment_id)]

    def get_or_404(self, contract_id: UUID) -> EnrollmentContract:
        contract = self.repo.get_by_id(contract_id)
        if not contract:
            raise not_found("Contrato não encontrado")
        return contract

    def issue(self, enrollment_id: UUID, data: ContractIssue, author_id: UUID) -> ContractOut:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        template = self.templates.get_or_404(data.template_id)
        if not template.is_active:
            raise conflict("Modelo de contrato inativo")
        term = self.terms.get_or_404(data.term_id) if data.term_id else None
        title = f"{template.name} — {enrollment.registration_number}{f' — {term.name}' if term else ''}"
        contract = self.repo.add(EnrollmentContract(
            program_enrollment_id=enrollment.id, template_id=template.id, term_id=term.id if term else None, kind=template.kind,
            title=title, body=render_template(template.body, self.fields.of(enrollment, term)),
            validation_code=validation_code(), created_by_id=author_id,
        ))
        self.repo.db.flush()
        contract.document_id = self.archive.archive(contract, author_id, "Emissão").id
        return to_out(self.repo.save(contract))

    def cancel(self, contract_id: UUID, author_id: UUID) -> ContractOut:
        contract = self.get_or_404(contract_id)
        if contract.status != ContractStatus.pending:
            raise conflict("Só contratos aguardando aceite podem ser cancelados")
        contract.status = ContractStatus.cancelled
        self.archive.archive(contract, author_id, "Cancelamento")
        return to_out(self.repo.save(contract))
