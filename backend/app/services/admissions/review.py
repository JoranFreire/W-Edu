from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.admissions import ApplicationStatus, SelectionMethod
from app.repositories.admissions import AdmissionApplicationRepository
from app.schemas.admissions import ApplicationOut, ApplicationReview
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.admissions.calls import AdmissionCallService
from app.services.admissions.views import application_out

BEFORE_SELECTION = (ApplicationStatus.submitted, ApplicationStatus.ineligible)


class ApplicationReviewService:
    """Analise das inscricoes pela secretaria antes da selecao: nota, reserva e aptidao."""

    def __init__(self, db: Session):
        self.repo = AdmissionApplicationRepository(db)
        self.calls = AdmissionCallService(db)

    def list(self, call_id: UUID) -> list[ApplicationOut]:
        self.calls.get_or_404(call_id)
        return [application_out(application) for application in self.repo.list_by_call(call_id)]

    def review(self, application_id: UUID, data: ApplicationReview) -> ApplicationOut:
        application = self.repo.get_by_id(application_id)
        if not application:
            raise not_found("Inscrição não encontrada")
        if application.status not in BEFORE_SELECTION:
            raise conflict("A análise só vale antes da seleção")
        if data.review_score is not None:
            if application.call.method != SelectionMethod.review:
                raise bad_request("Nota só se aplica à seleção por análise")
            application.review_score = data.review_score
        if data.reserved_verified is not None:
            application.reserved_verified = data.reserved_verified
        if data.eligible is True:
            application.status, application.ineligibility_reasons = ApplicationStatus.submitted, []
        elif data.eligible is False:
            if not data.reason:
                raise bad_request("Informe o motivo da inaptidão")
            application.status = ApplicationStatus.ineligible
            application.ineligibility_reasons = [*(application.ineligibility_reasons or []), data.reason]
        return application_out(self.repo.save(application))
