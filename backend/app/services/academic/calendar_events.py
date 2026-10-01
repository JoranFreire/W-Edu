from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import Session

from app.models.academic_calendar import CalendarEvent
from app.repositories.academic import CalendarEventRepository
from app.schemas.academic_calendar import CalendarEventCreate, CalendarEventUpdate, TermCalendarSummary
from app.services.academic.errors import bad_request, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.school_days import summarize
from app.services.academic.terms import AcademicTermService


class CalendarEventService:
    """Feriados, recessos, dias letivos extras, provas e eventos."""

    def __init__(self, db: Session):
        self.repo = CalendarEventRepository(db)
        self.terms = AcademicTermService(db)

    def list(self, term_id: UUID | None = None, start: date | None = None, end: date | None = None) -> list[CalendarEvent]:
        return self.repo.list(term_id=term_id, start=start, end=end)

    def create(self, data: CalendarEventCreate) -> CalendarEvent:
        event = CalendarEvent(**data.model_dump())
        self._validate_in_term(event)
        return self.repo.save(event)

    def update(self, event_id: UUID, data: CalendarEventUpdate) -> CalendarEvent:
        event = self.get_or_404(event_id)
        apply_patch(event, data, clearable=frozenset({"ends_on"}))
        if event.ends_on and event.ends_on < event.starts_on:
            raise bad_request("A data final não pode ser anterior à inicial")
        self._validate_in_term(event)
        return self.repo.save(event)

    def delete(self, event_id: UUID) -> None:
        self.repo.delete(self.get_or_404(event_id))

    def get_or_404(self, event_id: UUID) -> CalendarEvent:
        event = self.repo.get_by_id(event_id)
        if not event:
            raise not_found("Evento não encontrado")
        return event

    def summary(self, term_id: UUID) -> TermCalendarSummary:
        term = self.terms.get_or_404(term_id)
        events = self.repo.list(start=term.starts_on, end=term.ends_on)
        return summarize(term.starts_on, term.ends_on, events)

    def _validate_in_term(self, event: CalendarEvent) -> None:
        if event.term_id is None:
            return
        term = self.terms.get_or_404(event.term_id)
        if event.starts_on < term.starts_on or (event.ends_on or event.starts_on) > term.ends_on:
            raise bad_request("O evento precisa estar dentro do período letivo")
