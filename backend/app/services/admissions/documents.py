from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.storage import store_admission_document
from app.models.admissions import ApplicationDocument, ApplicationStatus
from app.models.student import Student
from app.repositories.admissions import AdmissionApplicationRepository, ApplicationDocumentRepository
from app.schemas.admissions import ApplicationOut, DocumentReviewInput
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.admissions.applications import ApplicationService
from app.services.admissions.views import application_out

OPEN_FOR_DOCUMENTS = (ApplicationStatus.submitted, ApplicationStatus.ineligible, ApplicationStatus.waitlisted, ApplicationStatus.selected)


class ApplicationDocumentService:
    """Comprovantes: o candidato envia, a secretaria confere e baixa."""

    def __init__(self, db: Session):
        self.repo = ApplicationDocumentRepository(db)
        self.applications = AdmissionApplicationRepository(db)
        self.applicant_side = ApplicationService(db)

    def upload(self, applicant: Student, application_id: int, kind: str, file: UploadFile) -> ApplicationOut:
        application = self.applicant_side.own(applicant, application_id)
        if application.status not in OPEN_FOR_DOCUMENTS:
            raise conflict("Inscrição encerrada para envio de comprovantes")
        try:
            path, name, _ = store_admission_document(application.id, file)
        except ValueError as exc:
            raise bad_request(str(exc)) from exc
        self.repo.save(ApplicationDocument(
            application_id=application.id, kind=kind.strip()[:120] or "Comprovante", file_name=name,
            mime_type=file.content_type, storage_path=path,
        ))
        self.applications.db.refresh(application)
        return application_out(application)

    def review(self, document_id: int, data: DocumentReviewInput, reviewer: Student) -> ApplicationOut:
        document = self._get_or_404(document_id)
        document.review, document.review_note, document.reviewed_by_id = data.review, data.note, reviewer.id
        self.repo.save(document)
        return application_out(document.application)

    def download(self, document_id: int) -> FileResponse:
        document = self._get_or_404(document_id)
        path = Path(document.storage_path)
        if not path.exists():
            raise not_found("Arquivo não encontrado")
        return FileResponse(path, filename=document.file_name, media_type=document.mime_type or "application/octet-stream")

    def _get_or_404(self, document_id: int) -> ApplicationDocument:
        document = self.repo.get_by_id(document_id)
        if not document:
            raise not_found("Comprovante não encontrado")
        return document
