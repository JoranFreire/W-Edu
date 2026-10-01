from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.schedule import ClassEnrollment
from app.repositories.retention import RetentionAttendanceRepository
from app.services.retention.rules import Ledger, trailing


class AttendanceLedgerBuilder:
    """Frequencia por inscricao: pelo diario de classe, se a turma o usa (sem previsao de aulas futuras);
    senao pelos encontros encerrados, comparados com todos os encontros agendados."""

    def __init__(self, db: Session):
        self.repo = RetentionAttendanceRepository(db)

    def for_enrollments(self, offering_id: UUID, enrollments: list[ClassEnrollment]) -> dict[UUID, Ledger]:
        diary = self.repo.diary_sessions(offering_id)
        if diary:
            return {e.id: self._from_diary(diary, e.id) for e in enrollments}
        meetings = self.repo.closed_meetings_absent(offering_id)
        planned = self.repo.planned_meetings(offering_id)
        return {e.id: self._from_meetings(meetings, e.student_id, planned) for e in enrollments}

    @staticmethod
    def _from_diary(sessions, enrollment_id: UUID) -> Ledger:
        total = sum(lessons for lessons, _ in sessions)
        flags, absences = [], 0
        for _, rows in sessions:
            row = rows.get(enrollment_id)
            missed = row.absences if row and not row.justified else 0
            absences += missed
            flags.append(missed > 0)
        return Ledger(total=total, absences=absences, trailing_absences=trailing(flags))

    @staticmethod
    def _from_meetings(meetings: list[set[UUID]], student_id: UUID, planned: int) -> Ledger:
        flags = [student_id in absent for absent in meetings]
        return Ledger(total=len(meetings), absences=sum(flags), trailing_absences=trailing(flags), planned=planned)
