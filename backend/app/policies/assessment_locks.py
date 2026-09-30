"""Bloqueio de edicao de notas e diario por etapa ou periodo letivo encerrado."""

from datetime import date

from fastapi import HTTPException, status

from app.models.academic_calendar import AcademicTerm, GradingPeriod, GradingPeriodStatus, TermStatus


def is_period_locked(period: GradingPeriod | None) -> bool:
    if period is None:
        return False
    return period.status == GradingPeriodStatus.closed or period.term.status == TermStatus.closed


def is_date_locked(term: AcademicTerm | None, day: date) -> bool:
    """Data do diario cai em periodo encerrado ou em etapa encerrada."""
    if term is None:
        return False
    if term.status == TermStatus.closed:
        return True
    return any(p.status == GradingPeriodStatus.closed and p.starts_on <= day <= p.ends_on for p in term.grading_periods)


def ensure_unlocked(locked: bool, detail: str = "Etapa encerrada; lançamentos bloqueados") -> None:
    if locked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
