"""Indicadores e perfil da prestacao de contas (funcoes puras)."""

from collections import Counter
from datetime import date

from app.models.admissions import Schooling
from app.models.schedule import ClassEnrollment, ClassEnrollmentResult, ClassEnrollmentStatus
from app.services.admissions.rules import age_on

AGE_BRACKETS = ((0, 17, "até 17"), (18, 24, "18 a 24"), (25, 29, "25 a 29"), (30, 39, "30 a 39"), (40, 59, "40 a 59"), (60, 200, "60 ou mais"))
# Faixas de renda por pessoa em fracoes do salario minimo informado no relatorio.
INCOME_BRACKETS = ((0.25, "até 1/4 SM"), (0.5, "1/4 a 1/2 SM"), (1.0, "1/2 a 1 SM"), (float("inf"), "acima de 1 SM"))


def outcome(enrollment: ClassEnrollment) -> str:
    """Situacao da matricula: desligado (faltas), desistente, concluinte ou ativo."""
    if enrollment.dismissed_at is not None:
        return "dismissed"
    if enrollment.status == ClassEnrollmentStatus.cancelled:
        return "dropped"
    if enrollment.status == ClassEnrollmentStatus.completed or enrollment.result == ClassEnrollmentResult.approved:
        return "completed"
    return "active"


def indicators(enrollments: list[ClassEnrollment]) -> dict[str, float]:
    counts = Counter(outcome(e) for e in enrollments)
    total = len(enrollments)
    lost = counts["dismissed"] + counts["dropped"]
    return {
        "enrolled": total, "active": counts["active"], "completed": counts["completed"], "dismissed": counts["dismissed"],
        "dropped": counts["dropped"], "evasion_rate": round(100 * lost / total, 1) if total else 0.0,
    }


def age_bracket(birth_date: date, reference: date) -> str:
    age = age_on(birth_date, reference)
    return next(label for low, high, label in AGE_BRACKETS if low <= age <= high)


def income_bracket(per_capita_cents: float, minimum_wage_cents: int) -> str:
    share = per_capita_cents / minimum_wage_cents
    return next(label for limit, label in INCOME_BRACKETS if share <= limit)


def profile_counts(answers: list[tuple[date, Schooling, int, int, bool]], reference: date, minimum_wage_cents: int) -> dict:
    """Respostas (nascimento, escolaridade, renda familiar, pessoas, vaga reservada) agregadas por faixa."""
    age = Counter(age_bracket(birth, reference) for birth, _, _, _, _ in answers)
    income = Counter(income_bracket(total / max(people, 1), minimum_wage_cents) for _, _, total, people, _ in answers)
    schooling = Counter(level.value for _, level, _, _, _ in answers)
    return {
        "respondents": len(answers),
        "age": {label: age.get(label, 0) for _, _, label in AGE_BRACKETS},
        "income_per_capita": {label: income.get(label, 0) for _, label in INCOME_BRACKETS},
        "schooling": {level.value: schooling.get(level.value, 0) for level in Schooling},
        "reserved_seats": sum(1 for *_, reserved in answers if reserved),
    }
