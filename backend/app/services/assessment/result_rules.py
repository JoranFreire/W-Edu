"""Resultado final da disciplina (funcao pura).

Recuperacao substitutiva: vale a maior nota entre a media e a recuperacao.
Frequencia abaixo do minimo reprova por falta, qualquer que seja a nota.
"""

from dataclasses import dataclass

from app.models.schedule import ClassEnrollmentResult as Result
from app.schemas.assessment import GradingSchemeOut


@dataclass(frozen=True)
class FinalOutcome:
    final_grade: float | None
    result: Result


def decide(average: float | None, recovery_score: float | None, attendance_rate: float | None, scheme: GradingSchemeOut) -> FinalOutcome:
    grade = average
    if recovery_score is not None and scheme.recovery_enabled:
        grade = recovery_score if grade is None else max(grade, recovery_score)
    if grade is None:
        return FinalOutcome(None, Result.in_progress)
    if attendance_rate is not None and attendance_rate < scheme.min_attendance:
        return FinalOutcome(grade, Result.failed_attendance)
    if grade >= scheme.passing_grade:
        return FinalOutcome(grade, Result.approved)
    if scheme.recovery_enabled and recovery_score is None:
        return FinalOutcome(grade, Result.recovery)
    return FinalOutcome(grade, Result.failed)


RESULT_LABELS = {
    Result.in_progress: "em andamento",
    Result.recovery: "em recuperação",
    Result.approved: "aprovado",
    Result.failed: "reprovado",
    Result.failed_attendance: "reprovado por falta",
}
