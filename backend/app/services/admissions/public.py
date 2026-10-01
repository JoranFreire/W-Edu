from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.admissions import AdmissionCallStatus
from app.repositories.admissions import AdmissionApplicationRepository, AdmissionCallRepository
from app.schemas.admissions import AdmissionCallOut, AdmissionResultOut, ResultEntry
from app.services.academic.errors import not_found
from app.services.admissions.calls import AdmissionCallService, to_out


class PublicAdmissionsService:
    """Catalogo publico de editais e resultado por protocolo (sem nomes), com a semente do sorteio."""

    def __init__(self, db: Session):
        self.repo = AdmissionCallRepository(db)
        self.applications = AdmissionApplicationRepository(db)
        self.calls = AdmissionCallService(db)

    def catalog(self) -> list[AdmissionCallOut]:
        calls = self.repo.list_published()
        counts = self.applications.count_by_call([call.id for call in calls])
        return [to_out(call, counts.get(call.id, 0)) for call in calls]

    def detail(self, call_id: int) -> AdmissionCallOut:
        call = self.calls.get_or_404(call_id)
        if call.status == AdmissionCallStatus.draft:
            raise not_found("Edital não encontrado")
        return self.calls.detail(call_id)

    def result(self, call_id: int) -> AdmissionResultOut:
        call = self.calls.get_or_404(call_id)
        if call.status != AdmissionCallStatus.selected:
            raise not_found("Resultado ainda não publicado")
        entries = [
            ResultEntry(protocol=a.protocol, rank=a.rank, status=a.status, seat_kind=a.seat_kind)
            for a in self.applications.list_by_call(call.id) if a.rank is not None
        ]
        return AdmissionResultOut(
            call_id=call.id, title=call.title, method=call.method, lottery_seed=call.lottery_seed,
            selected_at=call.selected_at, entries=entries,
        )
