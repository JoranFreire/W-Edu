from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic import Subject, SubjectEquivalence
from app.repositories.academic import SubjectEquivalenceRepository
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.subjects import SubjectService


class SubjectEquivalenceService:
    """Equivalencias sao simetricas: A equivale a B implica B equivale a A."""

    def __init__(self, db: Session):
        self.repo = SubjectEquivalenceRepository(db)
        self.subjects = SubjectService(db)

    def list(self, subject_id: int) -> list[Subject]:
        self.subjects.get_or_404(subject_id)
        return self.repo.list_equivalents(subject_id)

    def add(self, subject_id: int, other_id: int) -> Subject:
        if subject_id == other_id:
            raise bad_request("Disciplina não pode ser equivalente a ela mesma")
        self.subjects.get_or_404(subject_id)
        other = self.subjects.get_or_404(other_id)
        if self.repo.get_link(subject_id, other_id):
            raise conflict("Equivalência já cadastrada")
        low, high = sorted((subject_id, other_id))
        self.repo.save(SubjectEquivalence(subject_id=low, equivalent_subject_id=high))
        return other

    def remove(self, subject_id: int, other_id: int) -> None:
        link = self.repo.get_link(subject_id, other_id)
        if not link:
            raise not_found("Equivalência não encontrada")
        self.repo.delete(link)
