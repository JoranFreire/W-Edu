"""Transicoes de status permitidas (regras puras)."""

from app.models.academic_calendar import TermStatus
from app.models.academic_groups import ProgramEnrollmentStatus as Enrollment

TERM_TRANSITIONS: dict[TermStatus, set[TermStatus]] = {
    TermStatus.planned: {TermStatus.open},
    TermStatus.open: {TermStatus.closed},
    TermStatus.closed: {TermStatus.open},  # reabertura para correcoes
}

ENROLLMENT_TRANSITIONS: dict[Enrollment, set[Enrollment]] = {
    Enrollment.active: {Enrollment.locked, Enrollment.graduated, Enrollment.dropped, Enrollment.transferred, Enrollment.cancelled},
    Enrollment.locked: {Enrollment.active, Enrollment.dropped, Enrollment.transferred, Enrollment.cancelled},
    Enrollment.graduated: set(),
    Enrollment.dropped: set(),
    Enrollment.transferred: set(),
    Enrollment.cancelled: set(),
}


def can_change_term(current: TermStatus, target: TermStatus) -> bool:
    return target in TERM_TRANSITIONS[current]


def can_change_enrollment(current: Enrollment, target: Enrollment) -> bool:
    return target in ENROLLMENT_TRANSITIONS[current]
