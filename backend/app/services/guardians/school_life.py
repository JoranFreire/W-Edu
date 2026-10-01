from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.school_life import StudentOccurrence
from app.models.student import Student
from app.policies.guardian_access import ensure_linked
from app.repositories.guardians import GuardianLinkRepository
from app.repositories.school_life import OccurrenceRepository
from app.schemas.school_life import AgendaItemOut
from app.services.academic.errors import not_found
from app.services.school_life.agenda import AgendaService


class GuardianSchoolLifeService:
    """Portal do responsavel: ocorrencias (com ciencia) e agenda da turma do dependente."""

    def __init__(self, db: Session):
        self.links = GuardianLinkRepository(db)
        self.occurrences = OccurrenceRepository(db)
        self.agenda = AgendaService(db)

    def occurrences_of(self, guardian: Student, student_id: int) -> list[StudentOccurrence]:
        self._ensure_dependent(guardian, student_id)
        return self.occurrences.list_by_student(student_id)

    def acknowledge(self, guardian: Student, student_id: int, occurrence_id: int) -> StudentOccurrence:
        self._ensure_dependent(guardian, student_id)
        occurrence = self.occurrences.get_by_id(occurrence_id)
        if not occurrence or occurrence.student_id != student_id:
            raise not_found("Ocorrência não encontrada")
        if occurrence.acknowledged_at is None:
            occurrence.acknowledged_by_id = guardian.id
            occurrence.acknowledged_at = datetime.now(timezone.utc)
        return self.occurrences.save(occurrence)

    def agenda_of(self, guardian: Student, student_id: int, from_date: date | None = None) -> list[AgendaItemOut]:
        self._ensure_dependent(guardian, student_id)
        return self.agenda.for_student(student_id, from_date)

    def _ensure_dependent(self, guardian: Student, student_id: int) -> None:
        ensure_linked(self.links.get(student_id, guardian.id))
