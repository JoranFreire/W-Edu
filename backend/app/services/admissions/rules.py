"""Regras do processo seletivo (funcoes puras): requisitos, classificacao e distribuicao das vagas."""

from uuid import UUID
from dataclasses import dataclass
from datetime import date, datetime
import random
import unicodedata

from app.models.admissions import Schooling, SeatKind, SelectionMethod

SCHOOLING_ORDER = list(Schooling)


@dataclass(frozen=True)
class Requirements:
    min_age: int | None
    max_age: int | None
    min_schooling: Schooling | None
    max_income_per_capita_cents: int | None
    required_city: str | None


@dataclass(frozen=True)
class Answers:
    birth_date: date
    schooling: Schooling
    family_income_cents: int
    household_size: int
    city: str


def age_on(birth_date: date, day: date) -> int:
    return day.year - birth_date.year - ((day.month, day.day) < (birth_date.month, birth_date.day))


def _plain(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").strip().casefold()


def ineligibility(requirements: Requirements, answers: Answers, reference_day: date) -> list[str]:
    """Motivos pelos quais a inscricao nao atende ao edital (vazio: apta). A idade vale no fim das inscricoes."""
    reasons = []
    age = age_on(answers.birth_date, reference_day)
    if requirements.min_age is not None and age < requirements.min_age:
        reasons.append(f"Idade mínima de {requirements.min_age} anos")
    if requirements.max_age is not None and age > requirements.max_age:
        reasons.append(f"Idade máxima de {requirements.max_age} anos")
    if requirements.min_schooling is not None and SCHOOLING_ORDER.index(answers.schooling) < SCHOOLING_ORDER.index(requirements.min_schooling):
        reasons.append("Escolaridade abaixo da exigida")
    if requirements.max_income_per_capita_cents is not None:
        per_capita = answers.family_income_cents / max(answers.household_size, 1)
        if per_capita > requirements.max_income_per_capita_cents:
            reasons.append("Renda por pessoa acima do limite")
    if requirements.required_city and _plain(answers.city) != _plain(requirements.required_city):
        reasons.append(f"Exige morar em {requirements.required_city}")
    return reasons


@dataclass(frozen=True)
class Candidate:
    id: UUID
    applied_at: datetime
    score: float | None
    reserved: bool   # concorre a reserva (declarou e a conferencia nao recusou)


def rank(candidates: list[Candidate], method: SelectionMethod, seed: str | None = None) -> list[Candidate]:
    """Ordem de classificacao: inscricao, nota (empate pela inscricao) ou sorteio reproduzivel pela semente."""
    if method == SelectionMethod.review:
        return sorted(candidates, key=lambda c: (-(c.score if c.score is not None else float("-inf")), c.applied_at, c.id))
    if method == SelectionMethod.lottery:
        drawn = sorted(candidates, key=lambda c: c.id)
        random.Random(seed).shuffle(drawn)
        return drawn
    return sorted(candidates, key=lambda c: (c.applied_at, c.id))


def fill(ordered: list[Candidate], reserved_vacancies: int, general_vacancies: int) -> list[tuple[Candidate, SeatKind]]:
    """Preenche primeiro a reserva com quem concorre a ela; a reserva que sobra vira ampla concorrencia."""
    chosen: list[tuple[Candidate, SeatKind]] = []
    reserved = [c for c in ordered if c.reserved][:max(reserved_vacancies, 0)]
    chosen += [(c, SeatKind.reserved) for c in reserved]
    taken = {c.id for c in reserved}
    general = max(general_vacancies, 0) + max(reserved_vacancies, 0) - len(reserved)
    chosen += [(c, SeatKind.general) for c in [c for c in ordered if c.id not in taken][:general]]
    return chosen
