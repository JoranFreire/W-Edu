"""Regras da matricula por disciplina (funcoes puras)."""

from dataclasses import dataclass, field
from datetime import datetime, time, timezone


def as_utc(moment: datetime) -> datetime:
    """Data em UTC; sem fuso (como o SQLite devolve) ela ja esta em UTC."""
    return moment.astimezone(timezone.utc) if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def window_is_open(opens_at: datetime, closes_at: datetime, now: datetime) -> bool:
    return as_utc(opens_at) <= now < as_utc(closes_at)


@dataclass(frozen=True)
class WeeklySlot:
    weekday: int
    starts: time
    ends: time


def overlaps(first: WeeklySlot, second: WeeklySlot) -> bool:
    return first.weekday == second.weekday and first.starts < second.ends and second.starts < first.ends


def clashing(target: list[WeeklySlot], taken: dict[str, list[WeeklySlot]]) -> list[str]:
    """Nomes das ofertas ja cursadas no periodo que se sobrepoem a algum horario da nova."""
    return sorted(name for name, slots in taken.items() if any(overlaps(a, b) for a in target for b in slots))


def missing_prerequisites(required: dict[int, str], done: set[int]) -> list[str]:
    return sorted(name for subject_id, name in required.items() if subject_id not in done)


@dataclass(frozen=True)
class Evaluation:
    """Impedimentos da inscricao; `full` indica turma lotada (cabe lista de espera)."""

    blockers: list[str] = field(default_factory=list)
    full: bool = False


def evaluate(
    *,
    already_done: bool,
    same_subject_in: str | None,
    missing: list[str],
    clashes: list[str],
    credits: int,
    registered_credits: int,
    max_credits: int | None,
    seats_left: int,
) -> Evaluation:
    blockers = []
    if already_done:
        blockers.append("Disciplina já cursada ou aproveitada")
    if same_subject_in:
        blockers.append(f"Já inscrito nesta disciplina em {same_subject_in}")
    if missing:
        blockers.append("Pré-requisito pendente: " + ", ".join(missing))
    if clashes:
        blockers.append("Choque de horário com " + ", ".join(clashes))
    if max_credits is not None and registered_credits + credits > max_credits:
        blockers.append(f"Ultrapassa o limite de {max_credits} créditos no período")
    return Evaluation(blockers=blockers, full=seats_left <= 0)
