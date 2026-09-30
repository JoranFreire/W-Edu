"""Contagem de dias letivos de um periodo a partir dos eventos do calendario (funcao pura)."""

from collections.abc import Iterable
from datetime import date, timedelta

from app.models.academic_calendar import CalendarEvent, CalendarEventKind
from app.schemas.academic_calendar import TermCalendarSummary

NON_SCHOOL = {CalendarEventKind.holiday, CalendarEventKind.recess}


def _days(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _event_days(event: CalendarEvent, start: date, end: date) -> set[date]:
    first, last = max(event.starts_on, start), min(event.ends_on or event.starts_on, end)
    return set(_days(first, last)) if first <= last else set()


def summarize(starts_on: date, ends_on: date, events: Iterable[CalendarEvent]) -> TermCalendarSummary:
    """Dias uteis (seg-sex) menos feriados/recessos, mais dias letivos extras (ex.: sabados)."""
    closed: set[date] = set()
    extra: set[date] = set()
    exams = 0
    for event in events:
        days = _event_days(event, starts_on, ends_on)
        if event.kind in NON_SCHOOL:
            closed |= days
        elif event.kind == CalendarEventKind.school_day:
            extra |= days
        elif event.kind == CalendarEventKind.exam and days:
            exams += 1
    weekdays = {day for day in _days(starts_on, ends_on) if day.weekday() < 5}
    extra_days = extra - weekdays - closed
    school = (weekdays - closed) | extra_days
    return TermCalendarSummary(
        school_days=len(school),
        non_school_days=len(weekdays & closed),
        extra_school_days=len(extra_days),
        exams=exams,
    )
