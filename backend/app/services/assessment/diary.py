from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.class_diary import ClassDiaryEntry
from app.models.schedule import ClassOffering
from app.models.student import Student
from app.policies.assessment_locks import ensure_offering_open, ensure_unlocked, is_date_locked, is_offering_finalized
from app.repositories.assessment import ClassDiaryRepository, PeriodClosureRepository
from app.repositories.schedule import ScheduledMeetingRepository
from app.schemas.assessment import DiaryEntryCreate, DiaryEntryOut, DiaryEntryUpdate
from app.services.academic.patch import apply_patch
from app.services.assessment.errors import bad_request, conflict, not_found
from app.services.assessment.offerings import TeachingOfferingService


class ClassDiaryService:
    """Registro de aulas: data, quantidade de aulas e conteudo ministrado."""

    def __init__(self, db: Session):
        self.repo = ClassDiaryRepository(db)
        self.meetings = ScheduledMeetingRepository(db)
        self.closures = PeriodClosureRepository(db)
        self.offerings = TeachingOfferingService(db)

    def list(self, offering_id: int, user: Student) -> list[DiaryEntryOut]:
        offering = self.offerings.get_for_teaching(offering_id, user)
        closed = self.closures.closed_period_ids(offering_id)
        return [self.to_out(entry, offering, closed) for entry in self.repo.list_by_offering(offering_id)]

    def create(self, offering_id: int, data: DiaryEntryCreate, user: Student) -> DiaryEntryOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        self._validate_date(offering, data)
        ensure_unlocked(is_date_locked(offering.term, data.date, self.closures.closed_period_ids(offering_id)))
        if self.repo.get_by_date(offering_id, data.date):
            raise conflict("Já existe registro de aula nesta data")
        entry = ClassDiaryEntry(class_offering_id=offering_id, instructor_id=user.id, **data.model_dump())
        return self.to_out(self.repo.save(entry), offering, set())

    def get_for_teaching(self, entry_id: int, user: Student) -> tuple[ClassDiaryEntry, ClassOffering]:
        entry = self.repo.get_by_id(entry_id)
        if not entry:
            raise not_found("Registro de aula não encontrado")
        return entry, self.offerings.get_for_teaching(entry.class_offering_id, user)

    def get_editable(self, entry_id: int, user: Student) -> tuple[ClassDiaryEntry, ClassOffering]:
        entry, offering = self.get_for_teaching(entry_id, user)
        ensure_offering_open(offering)
        ensure_unlocked(is_date_locked(offering.term, entry.date, self.closures.closed_period_ids(offering.id)))
        return entry, offering

    def update(self, entry_id: int, data: DiaryEntryUpdate, user: Student) -> DiaryEntryOut:
        entry, offering = self.get_editable(entry_id, user)
        if data.lesson_count is not None and any(a.absences > data.lesson_count for a in entry.attendance):
            raise bad_request("Há faltas acima da nova quantidade de aulas")
        apply_patch(entry, data)
        return self.to_out(self.repo.save(entry), offering, set())

    def delete(self, entry_id: int, user: Student) -> None:
        entry, _ = self.get_editable(entry_id, user)
        self.repo.delete(entry)

    @staticmethod
    def to_out(entry: ClassDiaryEntry, offering: ClassOffering, closed_in_offering: set[int]) -> DiaryEntryOut:
        return DiaryEntryOut(
            id=entry.id,
            class_offering_id=entry.class_offering_id,
            date=entry.date,
            lesson_count=entry.lesson_count,
            content_taught=entry.content_taught,
            instructor_id=entry.instructor_id,
            scheduled_meeting_id=entry.scheduled_meeting_id,
            locked=is_offering_finalized(offering) or is_date_locked(offering.term, entry.date, closed_in_offering),
        )

    def _validate_date(self, offering: ClassOffering, data: DiaryEntryCreate) -> None:
        term = offering.term
        if term and not term.starts_on <= data.date <= term.ends_on:
            raise bad_request("Data fora do período letivo da turma")
        if data.scheduled_meeting_id is not None:
            meeting = self.meetings.get_by_id(data.scheduled_meeting_id)
            if not meeting or meeting.class_offering_id != offering.id:
                raise not_found("Encontro não encontrado nesta turma")
