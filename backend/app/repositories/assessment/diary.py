from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy import func

from app.models.class_diary import ClassDiaryEntry, DiaryAttendance
from app.models.schedule import AttendanceRecord, AttendanceStatus
from app.repositories.academic._base import Repository


class ClassDiaryRepository(Repository[ClassDiaryEntry]):
    model = ClassDiaryEntry

    def list_by_offering(self, offering_id: UUID) -> list[ClassDiaryEntry]:
        return (
            self.db.query(ClassDiaryEntry)
            .filter(ClassDiaryEntry.class_offering_id == offering_id)
            .order_by(ClassDiaryEntry.date.desc())
            .all()
        )

    def get_by_date(self, offering_id: UUID, day: date) -> ClassDiaryEntry | None:
        return (
            self.db.query(ClassDiaryEntry)
            .filter(ClassDiaryEntry.class_offering_id == offering_id, ClassDiaryEntry.date == day)
            .first()
        )

    def total_lessons(self, offering_id: UUID) -> int:
        total = (
            self.db.query(func.coalesce(func.sum(ClassDiaryEntry.lesson_count), 0))
            .filter(ClassDiaryEntry.class_offering_id == offering_id)
            .scalar()
        )
        return int(total or 0)


class DiaryAttendanceRepository(Repository[DiaryAttendance]):
    model = DiaryAttendance

    def by_entry(self, entry_id: UUID) -> dict[UUID, DiaryAttendance]:
        rows = self.db.query(DiaryAttendance).filter(DiaryAttendance.diary_entry_id == entry_id).all()
        return {row.class_enrollment_id: row for row in rows}

    def unjustified_absences(self, offering_id: UUID, start: date | None = None, end: date | None = None) -> dict[UUID, int]:
        """Faltas nao justificadas por inscricao, opcionalmente num intervalo de datas (etapa)."""
        query = (
            self.db.query(DiaryAttendance.class_enrollment_id, func.sum(DiaryAttendance.absences))
            .join(ClassDiaryEntry, DiaryAttendance.diary_entry_id == ClassDiaryEntry.id)
            .filter(ClassDiaryEntry.class_offering_id == offering_id, DiaryAttendance.justified.is_(False))
        )
        if start is not None:
            query = query.filter(ClassDiaryEntry.date >= start)
        if end is not None:
            query = query.filter(ClassDiaryEntry.date <= end)
        rows = query.group_by(DiaryAttendance.class_enrollment_id).all()
        return {enrollment_id: int(total or 0) for enrollment_id, total in rows}

    def absent_students_in_meeting(self, meeting_id: UUID) -> set[UUID]:
        """Alunos marcados ausentes no encontro agendado (presenca por QR/manual)."""
        rows = (
            self.db.query(AttendanceRecord.student_id)
            .filter(AttendanceRecord.scheduled_meeting_id == meeting_id, AttendanceRecord.status == AttendanceStatus.absent)
            .all()
        )
        return {row[0] for row in rows}
