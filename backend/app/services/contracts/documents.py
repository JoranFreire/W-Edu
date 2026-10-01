from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.pdf import render_paged_pdf
from app.core.storage import store_generated_document
from app.models.contracts import ContractStatus, EnrollmentContract
from app.models.document import Document, DocumentStatus, DocumentType, DocumentVersion
from app.repositories.document import DocumentRepository, DocumentVersionRepository


def contract_pdf(contract: EnrollmentContract) -> bytes:
    """Texto do contrato em paragrafos e rodape com o codigo de validacao e o aceite."""
    paragraphs = [block.strip().replace("\n", " ") for block in contract.body.split("\n\n") if block.strip()]
    footer = [f"Codigo de validacao: {contract.validation_code}"]
    if contract.status == ContractStatus.signed and contract.signed_at:
        footer.append(f"Aceito eletronicamente por {contract.signer.name if contract.signer else ''} em {contract.signed_at:%d/%m/%Y %H:%M} (UTC)")
    elif contract.status == ContractStatus.cancelled:
        footer.insert(0, "CONTRATO CANCELADO")
    else:
        footer.append("Aguardando aceite")
    return render_paged_pdf(contract.title, paragraphs, footer)


class ContractArchive:
    """Guarda o contrato no GED: documento do aluno com uma versao em PDF a cada mudanca (emissao, aceite)."""

    def __init__(self, db: Session):
        self.documents = DocumentRepository(db)
        self.versions = DocumentVersionRepository(db)

    def archive(self, contract: EnrollmentContract, author_id: UUID | None, note: str) -> Document:
        document = self.documents.get_by_id(contract.document_id) if contract.document_id else None
        if document is None:
            document = self.documents.create(Document(
                title=contract.title, document_type=DocumentType.contract, status=DocumentStatus.active,
                student_id=contract.program_enrollment.student_id, uploaded_by_id=author_id, external_reference=contract.validation_code,
            ))
        number = (document.latest_version_number or 0) + 1
        path, size = store_generated_document(document.id, number, f"contrato_{contract.validation_code}.pdf", contract_pdf(contract))
        self.versions.create(DocumentVersion(
            document_id=document.id, version_number=number, file_name=f"contrato_{contract.validation_code}.pdf",
            mime_type="application/pdf", file_size=size, storage_path=path, notes=note, created_by_id=author_id,
        ))
        document.latest_version_number = number
        if contract.status == ContractStatus.signed:
            document.is_signed, document.signed_at = True, contract.signed_at
            document.signed_by = contract.signer.name if contract.signer else None
        if contract.status == ContractStatus.cancelled:
            document.status = DocumentStatus.archived
        document.updated_at = datetime.now(timezone.utc)
        return self.documents.update(document)
