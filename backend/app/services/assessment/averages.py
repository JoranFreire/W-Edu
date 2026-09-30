"""Calculo de medias e conceitos (funcoes puras)."""

from collections.abc import Iterable
from dataclasses import dataclass

from app.models.assessment import AverageFormula


@dataclass(frozen=True)
class ScoredItem:
    score: float | None
    max_score: float
    weight: float


def normalize(score: float, max_score: float, scale_min: float, scale_max: float) -> float:
    """Leva a nota do item (0..max_score) para a escala do esquema."""
    return scale_min + (score / max_score) * (scale_max - scale_min)


def average(items: Iterable[ScoredItem], formula: AverageFormula, scale_min: float, scale_max: float) -> float | None:
    """Media dos itens ja avaliados; itens sem nota nao entram. None se nenhum tiver nota."""
    graded = [item for item in items if item.score is not None]
    if not graded:
        return None
    values = [normalize(item.score, item.max_score, scale_min, scale_max) for item in graded]  # type: ignore[arg-type]
    if formula == AverageFormula.arithmetic:
        return round(sum(values) / len(values), 2)
    total_weight = sum(item.weight for item in graded)
    if total_weight == 0:
        return round(sum(values) / len(values), 2)
    return round(sum(value * item.weight for value, item in zip(values, graded)) / total_weight, 2)


def mean_of(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return round(sum(present) / len(present), 2) if present else None


def concept_for(value: float | None, concepts: list[dict]) -> str | None:
    """Primeira faixa (da maior para a menor) cujo minimo a nota atinge."""
    if value is None or not concepts:
        return None
    for band in sorted(concepts, key=lambda band: band["min_value"], reverse=True):
        if value >= band["min_value"]:
            return band["code"]
    return None
