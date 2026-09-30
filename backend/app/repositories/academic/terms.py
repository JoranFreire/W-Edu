from __future__ import annotations

from datetime import date

from sqlalchemy import or_

from app.models.academic_calendar import AcademicTerm, CalendarEvent, GradingPeriod
from app.models.academic_groups import ClassGroup, ProgramEnrollment
from app.models.schedule import ClassOffering
from app.repositories.academic._base import Repository


class AcademicTermRepository(Repository[AcademicTerm]):
    model = AcademicTerm

    def list_all(self) -> list[AcademicTerm]:
        return self.db.query(AcademicTerm).order_by(AcademicTerm.starts_on.desc()).all()

    def get_by_name(self, name: str) -> AcademicTerm | None:
        return self.db.query(AcademicTerm).filter(AcademicTerm.name == name).first()

    def is_referenced(self, term_id: int) -> bool:
        checks = (
            self.db.query(ClassGroup.id).filter(ClassGroup.term_id == term_id),
            self.db.query(ProgramEnrollment.id).filter(ProgramEnrollment.entry_term_id == term_id),
            self.db.query(ClassOffering.id).filter(ClassOffering.term_id == term_id),
        )
        return any(query.first() is not None for query in checks)


class GradingPeriodRepository(Repository[GradingPeriod]):
    model = GradingPeriod

    def list_by_term(self, term_id: int) -> list[GradingPeriod]:
        return self.db.query(GradingPeriod).filter(GradingPeriod.term_id == term_id).order_by(GradingPeriod.order).all()


class CalendarEventRepository(Repository[CalendarEvent]):
    model = CalendarEvent

    def list(self, term_id: int | None = None, start: date | None = None, end: date | None = None) -> list[CalendarEvent]:
        query = self.db.query(CalendarEvent)
        if term_id is not None:
            query = query.filter(CalendarEvent.term_id == term_id)
        if start is not None:
            query = query.filter(or_(CalendarEvent.starts_on >= start, CalendarEvent.ends_on >= start))
        if end is not None:
            query = query.filter(CalendarEvent.starts_on <= end)
        return query.order_by(CalendarEvent.starts_on, CalendarEvent.id).all()
