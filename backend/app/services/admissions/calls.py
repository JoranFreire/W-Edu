from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.admissions import AdmissionCall, AdmissionCallStatus
from app.repositories.admissions import AdmissionApplicationRepository, AdmissionCallRepository
from app.repositories.schedule import ClassOfferingRepository
from app.schemas.admissions import AdmissionCallCreate, AdmissionCallOut, AdmissionCallUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.registration.rules import as_utc, window_is_open

# Mudancas de situacao feitas a mao; a selecao publica o resultado (selected).
TRANSITIONS = {
    AdmissionCallStatus.draft: {AdmissionCallStatus.open},
    AdmissionCallStatus.open: {AdmissionCallStatus.closed, AdmissionCallStatus.draft},
    AdmissionCallStatus.closed: {AdmissionCallStatus.open},
}


def is_accepting(call: AdmissionCall) -> bool:
    return call.status == AdmissionCallStatus.open and window_is_open(call.opens_at, call.closes_at, datetime.now(timezone.utc))


def to_out(call: AdmissionCall, applications: int = 0) -> AdmissionCallOut:
    offering = call.class_offering
    return AdmissionCallOut(
        id=call.id, class_offering_id=offering.id, course_name=offering.course.name, offering_name=offering.name,
        starts_at=offering.starts_at, title=call.title, description=call.description, method=call.method, seats=call.seats,
        reserved_seats=call.reserved_seats, reserved_label=call.reserved_label, opens_at=call.opens_at, closes_at=call.closes_at,
        confirmation_days=call.confirmation_days, min_age=call.min_age, max_age=call.max_age, min_schooling=call.min_schooling,
        max_income_per_capita_cents=call.max_income_per_capita_cents, required_city=call.required_city,
        required_documents=list(call.required_documents or []), status=call.status, is_accepting=is_accepting(call),
        lottery_seed=call.lottery_seed, applications=applications,
    )


class AdmissionCallService:
    """Editais: cadastro pela secretaria, abertura e encerramento das inscricoes."""

    def __init__(self, db: Session):
        self.repo = AdmissionCallRepository(db)
        self.applications = AdmissionApplicationRepository(db)
        self.offerings = ClassOfferingRepository(db)

    def list(self) -> list[AdmissionCallOut]:
        calls = self.repo.list()
        counts = self.applications.count_by_call([call.id for call in calls])
        return [to_out(call, counts.get(call.id, 0)) for call in calls]

    def get_or_404(self, call_id: int) -> AdmissionCall:
        call = self.repo.get_by_id(call_id)
        if not call:
            raise not_found("Edital não encontrado")
        return call

    def detail(self, call_id: int) -> AdmissionCallOut:
        call = self.get_or_404(call_id)
        return to_out(call, self.applications.count_by_call([call.id]).get(call.id, 0))

    def create(self, data: AdmissionCallCreate) -> AdmissionCallOut:
        offering = self.offerings.get_by_id(data.class_offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        if data.seats > offering.capacity:
            raise bad_request("O edital não pode ter mais vagas que a turma")
        call = AdmissionCall(**data.model_dump())
        self._validate_window(call)
        return to_out(self.repo.save(call))

    def update(self, call_id: int, data: AdmissionCallUpdate) -> AdmissionCallOut:
        call = self.get_or_404(call_id)
        if call.status == AdmissionCallStatus.selected:
            raise conflict("Resultado já publicado")
        apply_patch(call, data)
        self._validate_window(call)
        return self.detail(self.repo.save(call).id)

    def change_status(self, call_id: int, status: AdmissionCallStatus) -> AdmissionCallOut:
        call = self.get_or_404(call_id)
        if status not in TRANSITIONS.get(call.status, set()):
            raise conflict("Mudança de situação não permitida")
        call.status = status
        return self.detail(self.repo.save(call).id)

    @staticmethod
    def _validate_window(call: AdmissionCall) -> None:
        call.opens_at, call.closes_at = as_utc(call.opens_at), as_utc(call.closes_at)
        if call.closes_at <= call.opens_at:
            raise bad_request("O encerramento deve ser posterior à abertura")
