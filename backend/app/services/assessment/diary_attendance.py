from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.class_diary import ClassDiaryEntry, DiaryAttendance
from app.models.student import Student
from app.repositories.assessment import DiaryAttendanceRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import DiaryAttendanceInput, DiaryAttendanceRow
from app.services.assessment.diary import ClassDiaryService
from app.services.assessment.errors import bad_request
from app.services.assessment.offerings import TeachingOfferingService


class DiaryAttendanceService:
    """Chamada de um registro de aula; sem lancamento, parte da presenca do encontro (QR/manual)."""

    def __init__(self, db: Session):
        self.repo = DiaryAttendanceRepository(db)
        self.diary = ClassDiaryService(db)
        self.offerings = TeachingOfferingService(db)

    def list(self, entry_id: UUID, user: Student) -> list[DiaryAttendanceRow]:
        entry, _ = self.diary.get_for_teaching(entry_id, user)
        stored = self.repo.by_entry(entry_id)
        absent = self._absent_from_meeting(entry)
        rows = []
        for enrollment in self.offerings.roster(entry.class_offering_id):
            row = stored.get(enrollment.id)
            default_absences = entry.lesson_count if enrollment.student_id in absent else 0
            rows.append(DiaryAttendanceRow(
                class_enrollment_id=enrollment.id,
                student=PersonSummary.model_validate(enrollment.student),
                absences=row.absences if row else default_absences,
                justified=row.justified if row else False,
                note=row.note if row else None,
            ))
        return rows

    def save(self, entry_id: UUID, values: list[DiaryAttendanceInput], user: Student) -> list[DiaryAttendanceRow]:
        entry, _ = self.diary.get_editable(entry_id, user)
        valid_ids = {e.id for e in self.offerings.roster(entry.class_offering_id)}
        stored = self.repo.by_entry(entry_id)
        for value in values:
            if value.class_enrollment_id not in valid_ids:
                raise bad_request("Aluno não pertence à turma")
            if value.absences > entry.lesson_count:
                raise bad_request(f"Faltas acima das aulas do dia ({entry.lesson_count})")
            row = stored.get(value.class_enrollment_id) or self.repo.add(
                DiaryAttendance(diary_entry_id=entry_id, class_enrollment_id=value.class_enrollment_id)
            )
            row.absences, row.justified, row.note = value.absences, value.justified, value.note
        self.repo.commit()
        return self.list(entry_id, user)

    def _absent_from_meeting(self, entry: ClassDiaryEntry) -> set[UUID]:
        if entry.scheduled_meeting_id is None:
            return set()
        return self.repo.absent_students_in_meeting(entry.scheduled_meeting_id)
