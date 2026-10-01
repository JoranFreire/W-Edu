"""Historico escolar, CR e integralizacao (funcoes puras)."""

from dataclasses import dataclass

from app.models.academic import ComponentKind
from app.models.schedule import ClassEnrollmentResult
from app.schemas.secretariat import TranscriptRow, TranscriptSummary


@dataclass(frozen=True)
class Component:
    subject_id: int
    code: str
    name: str
    term_number: int
    kind: ComponentKind
    hours: int
    credits: int | None


@dataclass(frozen=True)
class Attempt:
    """Cursada de uma disciplina da matriz (ou equivalente), em ordem cronologica."""

    subject_id: int
    grade: float | None
    result: ClassEnrollmentResult
    taken_in: str | None


@dataclass(frozen=True)
class Credit:
    subject_id: int
    grade: float | None
    source: str


def _status(attempts: list[Attempt], credit: Credit | None) -> tuple[str, float | None, str | None]:
    approved = [a for a in attempts if a.result == ClassEnrollmentResult.approved]
    if approved:
        last = approved[-1]
        return "completed", last.grade, last.taken_in
    if credit:
        return "credited", credit.grade, credit.source
    if any(a.result in (ClassEnrollmentResult.in_progress, ClassEnrollmentResult.recovery) for a in attempts):
        current = attempts[-1]
        return "in_progress", None, current.taken_in
    if attempts:
        last = attempts[-1]
        return "failed", last.grade, last.taken_in
    return "pending", None, None


def build_rows(components: list[Component], attempts: list[Attempt], credits: list[Credit]) -> list[TranscriptRow]:
    by_subject: dict[int, list[Attempt]] = {}
    for attempt in attempts:
        by_subject.setdefault(attempt.subject_id, []).append(attempt)
    credit_by_subject = {credit.subject_id: credit for credit in credits}
    rows = []
    for component in sorted(components, key=lambda c: (c.term_number, c.code)):
        tried = by_subject.get(component.subject_id, [])
        status, grade, taken_in = _status(tried, credit_by_subject.get(component.subject_id))
        rows.append(TranscriptRow(
            subject_id=component.subject_id, code=component.code, name=component.name, term_number=component.term_number,
            kind=component.kind, hours=component.hours, credits=component.credits,
            status=status, grade=grade, taken_in=taken_in, attempts=len(tried),
        ))
    return rows


def _weight(row: TranscriptRow) -> int:
    """Peso no CR: creditos, senao carga horaria."""
    return row.credits or row.hours or 1


def summarize(rows: list[TranscriptRow]) -> TranscriptSummary:
    done = [row for row in rows if row.status in ("completed", "credited")]
    graded = [row for row in done if row.grade is not None]
    total_weight = sum(_weight(row) for row in graded)
    mandatory = [row for row in rows if row.kind == ComponentKind.mandatory]
    mandatory_hours = sum(row.hours for row in mandatory)
    mandatory_done = sum(row.hours for row in done if row.kind == ComponentKind.mandatory)
    return TranscriptSummary(
        cr=round(sum(row.grade * _weight(row) for row in graded) / total_weight, 2) if total_weight else None,
        mandatory_hours=mandatory_hours,
        mandatory_hours_done=mandatory_done,
        elective_hours_done=sum(row.hours for row in done if row.kind != ComponentKind.mandatory),
        hours_done=sum(row.hours for row in done),
        integralization=round(100 * mandatory_done / mandatory_hours, 1) if mandatory_hours else 100.0,
        completed_components=len(done),
        total_components=len(rows),
        credits_done=sum(row.credits or 0 for row in done),
        mandatory_credits=sum(row.credits or 0 for row in mandatory),
    )
