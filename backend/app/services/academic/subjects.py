from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic import Subject
from app.repositories.academic import SubjectRepository
from app.schemas.academic import SubjectCreate, SubjectUpdate
from app.services.academic.errors import conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.course import CourseService

CLEARABLE = frozenset({"syllabus", "credits", "course_id"})


class SubjectService:
    def __init__(self, db: Session):
        self.repo = SubjectRepository(db)
        self.courses = CourseService(db)

    def list(self, search: str | None = None, active: bool | None = None) -> list[Subject]:
        return self.repo.list(search=search, active=active)

    def get_or_404(self, subject_id: UUID) -> Subject:
        subject = self.repo.get_by_id(subject_id)
        if not subject:
            raise not_found("Disciplina não encontrada")
        return subject

    def create(self, data: SubjectCreate) -> Subject:
        if data.course_id is not None:
            self.courses.get_or_404(data.course_id)
        self._ensure_unique_code(data.code)
        return self.repo.save(Subject(**data.model_dump()))

    def update(self, subject_id: UUID, data: SubjectUpdate) -> Subject:
        subject = self.get_or_404(subject_id)
        if data.course_id is not None:
            self.courses.get_or_404(data.course_id)
        if data.code is not None and data.code != subject.code:
            self._ensure_unique_code(data.code)
        apply_patch(subject, data, clearable=CLEARABLE)
        return self.repo.save(subject)

    def delete(self, subject_id: UUID) -> None:
        subject = self.get_or_404(subject_id)
        if self.repo.is_in_curriculum(subject_id):
            raise conflict("Disciplina faz parte de uma matriz curricular; desative-a em vez de excluir")
        self.repo.delete(subject)

    def _ensure_unique_code(self, code: str) -> None:
        if self.repo.get_by_code(code):
            raise conflict("Já existe disciplina com este código")
