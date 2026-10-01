from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.admissions import AdmissionApplication, AdmissionCall, ApplicationStatus
from app.models.student import Student
from app.repositories.admissions import AdmissionApplicationRepository
from app.schemas.admissions import ApplicationCreate, ApplicationOut
from app.services.academic.errors import conflict, not_found
from app.services.admissions.calls import AdmissionCallService, is_accepting
from app.services.admissions.rules import Answers, Requirements, ineligibility
from app.services.admissions.views import application_out


def requirements_of(call: AdmissionCall) -> Requirements:
    return Requirements(call.min_age, call.max_age, call.min_schooling, call.max_income_per_capita_cents, call.required_city)


def new_protocol() -> str:
    """Protocolo curto para o candidato anotar: ano e mes da inscricao e um trecho aleatorio."""
    return f"{datetime.now(timezone.utc):%y%m}-{secrets.token_hex(4).upper()}"


class ApplicationService:
    """Inscricao do candidato: questionario, conferencia automatica dos requisitos e desistencia antes da selecao."""

    def __init__(self, db: Session):
        self.repo = AdmissionApplicationRepository(db)
        self.calls = AdmissionCallService(db)

    def apply(self, applicant: Student, call_id: UUID, data: ApplicationCreate) -> ApplicationOut:
        call = self.calls.get_or_404(call_id)
        if not is_accepting(call):
            raise conflict("Inscrições encerradas ou ainda não abertas")
        if self.repo.get_for(call.id, applicant.id):
            raise conflict("Você já se inscreveu neste edital")
        answers = Answers(data.birth_date, data.schooling, data.family_income_cents, data.household_size, data.city)
        reasons = ineligibility(requirements_of(call), answers, call.closes_at.date())
        application = AdmissionApplication(
            call_id=call.id, applicant_id=applicant.id, protocol=new_protocol(),
            status=ApplicationStatus.ineligible if reasons else ApplicationStatus.submitted, ineligibility_reasons=reasons,
            **data.model_dump(),
        )
        if not call.reserved_seats:
            application.claims_reserved = False
        return application_out(self.repo.save(application))

    def list_mine(self, applicant: Student) -> list[ApplicationOut]:
        return [application_out(application) for application in self.repo.list_by_applicant(applicant.id)]

    def withdraw(self, applicant: Student, application_id: UUID) -> ApplicationOut:
        application = self.own(applicant, application_id)
        if application.status not in (ApplicationStatus.submitted, ApplicationStatus.ineligible):
            raise conflict("Depois da seleção, use a desistência da vaga")
        application.status = ApplicationStatus.withdrawn
        return application_out(self.repo.save(application))

    def own(self, applicant: Student, application_id: UUID) -> AdmissionApplication:
        application = self.repo.get_by_id(application_id)
        if not application or application.applicant_id != applicant.id:
            raise not_found("Inscrição não encontrada")
        return application
