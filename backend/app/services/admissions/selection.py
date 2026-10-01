from __future__ import annotations

from datetime import datetime, timezone
import secrets

from sqlalchemy.orm import Session

from app.models.admissions import AdmissionCallStatus, ApplicationStatus, SelectionMethod
from app.repositories.admissions import AdmissionApplicationRepository
from app.schemas.admissions import SelectionOut
from app.services.academic.errors import conflict
from app.services.admissions.calls import AdmissionCallService
from app.services.admissions.convocation import ConvocationService, candidate
from app.services.admissions.rules import fill, rank
from app.services.registration.rules import as_utc


class SelectionService:
    """Classifica as inscricoes aptas pela forma do edital, publica o resultado e convoca as vagas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AdmissionApplicationRepository(db)
        self.calls = AdmissionCallService(db)
        self.convocation = ConvocationService(db)

    def run(self, call_id: int) -> SelectionOut:
        call = self.calls.get_or_404(call_id)
        if call.status == AdmissionCallStatus.selected:
            raise conflict("Seleção já realizada")
        if call.status == AdmissionCallStatus.draft:
            raise conflict("Edital em rascunho")
        if call.status == AdmissionCallStatus.open and as_utc(call.closes_at) > datetime.now(timezone.utc):
            raise conflict("As inscrições ainda estão abertas")
        pool = self.repo.with_status(call.id, (ApplicationStatus.submitted,))
        if call.method == SelectionMethod.review and any(a.review_score is None for a in pool):
            raise conflict("Há inscrições aptas sem nota")
        seed = secrets.token_hex(16) if call.method == SelectionMethod.lottery else None
        ordered = rank([candidate(a) for a in pool], call.method, seed)
        by_id = {a.id: a for a in pool}
        for position, item in enumerate(ordered, start=1):
            by_id[item.id].rank, by_id[item.id].status = position, ApplicationStatus.waitlisted
        call.status, call.lottery_seed, call.selected_at = AdmissionCallStatus.selected, seed, datetime.now(timezone.utc)
        self.db.commit()
        called = self.convocation.summon(call, fill(ordered, call.reserved_seats, call.seats - call.reserved_seats))
        return SelectionOut(ranked=len(ordered), called=called, waitlisted=len(ordered) - called)
