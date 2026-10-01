"""Bloqueio de edicao de notas e diario.

Bloqueia quando a etapa foi encerrada na instituicao, fechada na turma, o periodo
letivo foi encerrado ou a turma foi finalizada.
"""

from uuid import UUID
from collections.abc import Collection
from datetime import date

from fastapi import HTTPException, status

from app.models.academic_calendar import AcademicTerm, GradingPeriod, GradingPeriodStatus, TermStatus
from app.models.schedule import ClassOffering, ClassStatus


def is_offering_finalized(offering: ClassOffering) -> bool:
    return offering.status == ClassStatus.completed


def is_period_locked(period: GradingPeriod | None, closed_in_offering: Collection[UUID] = ()) -> bool:
    if period is None:
        return False
    return (
        period.status == GradingPeriodStatus.closed
        or period.term.status == TermStatus.closed
        or period.id in closed_in_offering
    )


def is_date_locked(term: AcademicTerm | None, day: date, closed_in_offering: Collection[UUID] = ()) -> bool:
    """Data do diario cai em periodo encerrado ou em etapa encerrada/fechada na turma."""
    if term is None:
        return False
    if term.status == TermStatus.closed:
        return True
    return any(
        (p.status == GradingPeriodStatus.closed or p.id in closed_in_offering) and p.starts_on <= day <= p.ends_on
        for p in term.grading_periods
    )


def ensure_unlocked(locked: bool, detail: str = "Etapa encerrada; lançamentos bloqueados") -> None:
    if locked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def ensure_offering_open(offering: ClassOffering) -> None:
    ensure_unlocked(is_offering_finalized(offering), "Turma finalizada; lançamentos bloqueados")
