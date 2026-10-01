from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.school_life import StudentOccurrence
from app.models.student import Student
from app.policies.school_life_access import ensure_can_remove
from app.repositories.academic import ClassGroupRepository
from app.repositories.school_life import OccurrenceRepository
from app.schemas.school_life import OccurrenceCreate
from app.services.academic.errors import not_found
from app.services.school_life.family_notices import FamilyNoticeService
from app.services.school_life.students import SchoolStudentLookup


class OccurrenceService:
    """Registro de ocorrencias do aluno pela equipe escolar, com aviso a familia."""

    def __init__(self, db: Session):
        self.repo = OccurrenceRepository(db)
        self.groups = ClassGroupRepository(db)
        self.students = SchoolStudentLookup(db)
        self.notices = FamilyNoticeService(db)

    def list_for_student(self, student_id: int) -> list[StudentOccurrence]:
        self.students.get_or_404(student_id)
        return self.repo.list_by_student(student_id)

    def register(self, data: OccurrenceCreate, reporter: Student) -> StudentOccurrence:
        self.students.get_or_404(data.student_id)
        if data.class_group_id is not None and not self.groups.get_by_id(data.class_group_id):
            raise not_found("Turma não encontrada")
        occurrence = self.repo.add(StudentOccurrence(
            student_id=data.student_id, class_group_id=data.class_group_id, kind=data.kind, severity=data.severity,
            description=data.description, occurred_on=data.occurred_on or date.today(), reported_by_id=reporter.id,
        ))
        self.repo.db.flush()
        self.notices.occurrence_registered(occurrence)
        return self.repo.save(occurrence)

    def remove(self, occurrence_id: int, user: Student) -> None:
        occurrence = self.repo.get_by_id(occurrence_id)
        if not occurrence:
            raise not_found("Ocorrência não encontrada")
        ensure_can_remove(user, occurrence.reported_by_id)
        self.repo.delete(occurrence)
