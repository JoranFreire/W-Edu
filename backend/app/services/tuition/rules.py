"""Calculo das mensalidades (funcoes puras): vencimentos, descontos, multa e juros."""

import calendar
from dataclasses import dataclass
from datetime import date

from app.models.tuition import DiscountKind


@dataclass(frozen=True)
class Discount:
    kind: DiscountKind
    percent: float | None
    amount_cents: int | None


@dataclass(frozen=True)
class Composition:
    """Valor da parcela: bruto, descontos incondicionais e o desconto de pontualidade (condicional)."""

    gross: int
    discount: int
    punctuality: int

    @property
    def amount(self) -> int:
        return self.gross - self.discount


@dataclass(frozen=True)
class LateFeePolicy:
    fine_percent: float = 2.0             # multa sobre o valor em atraso
    monthly_interest_percent: float = 1.0  # juros de mora ao mes, pro rata die


@dataclass(frozen=True)
class Settlement:
    base: int
    punctuality: int
    fine: int
    interest: int

    @property
    def total(self) -> int:
        return self.base - self.punctuality + self.fine + self.interest


def due_dates(first_due_on: date, installments: int) -> list[date]:
    """Um vencimento por mes no mesmo dia (ou no ultimo dia do mes, quando ele for menor)."""
    dates = []
    for offset in range(installments):
        month_index = first_due_on.month - 1 + offset
        year, month = first_due_on.year + month_index // 12, month_index % 12 + 1
        dates.append(date(year, month, min(first_due_on.day, calendar.monthrange(year, month)[1])))
    return dates


def installment_gross(amount_cents: int, installments: int, credits: int | None) -> int:
    """Por credito: valor do credito vezes os creditos, dividido nas parcelas; senao, o valor da parcela."""
    if credits is None:
        return amount_cents
    return round(amount_cents * credits / installments)


def _value(discount: Discount, base: int) -> int:
    if discount.percent is not None:
        return round(base * discount.percent / 100)
    return discount.amount_cents or 0


def compose(gross: int, discounts: list[Discount]) -> Composition:
    """Descontos incondicionais somados (limitados ao bruto); pontualidade sobre o que sobra."""
    unconditional = min(gross, sum(_value(d, gross) for d in discounts if d.kind != DiscountKind.punctuality))
    remaining = gross - unconditional
    punctuality = min(remaining, sum(_value(d, remaining) for d in discounts if d.kind == DiscountKind.punctuality))
    return Composition(gross=gross, discount=unconditional, punctuality=punctuality)


def settle(amount: int, punctuality: int, due_on: date, paid_on: date, policy: LateFeePolicy) -> Settlement:
    """Ate o vencimento vale o desconto de pontualidade; depois, multa e juros diarios sobre o valor."""
    if paid_on <= due_on:
        return Settlement(base=amount, punctuality=punctuality, fine=0, interest=0)
    days = (paid_on - due_on).days
    return Settlement(
        base=amount, punctuality=0,
        fine=round(amount * policy.fine_percent / 100),
        interest=round(amount * policy.monthly_interest_percent / 100 * days / 30),
    )
