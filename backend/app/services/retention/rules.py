"""Risco de evasao (funcoes puras)."""

from dataclasses import dataclass
from typing import Literal

DEFAULT_LIMIT_PERCENT = 25.0
RiskLevel = Literal["ok", "attention", "exceeded"]


@dataclass(frozen=True)
class Ledger:
    """Presenca do aluno: sessoes dadas, sessoes previstas no curso, faltas e faltas seguidas mais recentes."""

    total: int
    absences: int
    trailing_absences: int
    planned: int = 0

    @property
    def absence_percent(self) -> float:
        """Faltas sobre as sessoes ja dadas (o que o aluno e a equipe acompanham)."""
        return round(100 * self.absences / self.total, 1) if self.total else 0.0

    @property
    def allowance_used_percent(self) -> float:
        """Faltas sobre todas as sessoes previstas: passa do limite quando ja nao da para cumprir a frequencia."""
        base = max(self.planned, self.total)
        return 100 * self.absences / base if base else 0.0


def level(ledger: Ledger, limit_percent: float | None) -> RiskLevel:
    """Faltas acima do limite sobre o curso inteiro: excedido; metade do limite no que ja foi dado ou duas seguidas: atencao."""
    limit = limit_percent or DEFAULT_LIMIT_PERCENT
    if ledger.allowance_used_percent > limit:
        return "exceeded"
    if ledger.absence_percent >= limit / 2 or ledger.trailing_absences >= 2:
        return "attention"
    return "ok"


def trailing(absent_flags: list[bool]) -> int:
    """Faltas seguidas no fim da sequencia (da sessao mais recente para tras)."""
    count = 0
    for absent in reversed(absent_flags):
        if not absent:
            break
        count += 1
    return count
