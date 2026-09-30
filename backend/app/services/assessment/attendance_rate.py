"""Percentual de frequencia (funcao pura)."""


def attendance_rate(total_lessons: int, absences: int) -> float | None:
    if total_lessons <= 0:
        return None
    return round(100 * max(total_lessons - absences, 0) / total_lessons, 1)
