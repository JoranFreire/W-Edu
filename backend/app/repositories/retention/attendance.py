from __future__ import annotations
from uuid import UUID

from app.models.class_diary import ClassDiaryEntry, DiaryAttendance
from app.models.schedule import AttendanceRecord, AttendanceStatus, ScheduledMeeting


class RetentionAttendanceRepository:
    """Sessoes da turma em ordem: aulas do diario (com faltas por aluno) ou encontros encerrados (com ausentes)."""

    def __init__(self, db):
        self.db = db

    def diary_sessions(self, offering_id: UUID) -> list[tuple[int, dict[UUID, DiaryAttendance]]]:
        entries = (
            self.db.query(ClassDiaryEntry)
            .filter(ClassDiaryEntry.class_offering_id == offering_id)
            .order_by(ClassDiaryEntry.date, ClassDiaryEntry.id)
            .all()
        )
        return [(entry.lesson_count, {row.class_enrollment_id: row for row in entry.attendance}) for entry in entries]

    def closed_meetings_absent(self, offering_id: UUID) -> list[set[UUID]]:
        """Para cada encontro encerrado, os alunos ausentes."""
        meetings = (
            self.db.query(ScheduledMeeting.id)
            .filter(ScheduledMeeting.class_offering_id == offering_id, ScheduledMeeting.is_closed.is_(True))
            .order_by(ScheduledMeeting.starts_at, ScheduledMeeting.id)
            .all()
        )
        absent_rows = (
            self.db.query(AttendanceRecord.scheduled_meeting_id, AttendanceRecord.student_id)
            .filter(AttendanceRecord.class_offering_id == offering_id, AttendanceRecord.status == AttendanceStatus.absent)
            .all()
        )
        absent: dict[UUID, set[UUID]] = {}
        for meeting_id, student_id in absent_rows:
            absent.setdefault(meeting_id, set()).add(student_id)
        return [absent.get(meeting_id, set()) for (meeting_id,) in meetings]

    def planned_meetings(self, offering_id: UUID) -> int:
        """Encontros agendados da turma (dados e futuros)."""
        return self.db.query(ScheduledMeeting.id).filter(ScheduledMeeting.class_offering_id == offering_id).count()
