from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic import Subject, SubjectPrerequisite
from app.repositories.academic import SubjectPrerequisiteRepository
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.graph import reaches
from app.services.academic.subjects import SubjectService


class SubjectPrerequisiteService:
    def __init__(self, db: Session):
        self.repo = SubjectPrerequisiteRepository(db)
        self.subjects = SubjectService(db)

    def list(self, subject_id: int) -> list[Subject]:
        self.subjects.get_or_404(subject_id)
        return self.repo.list_required(subject_id)

    def add(self, subject_id: int, required_subject_id: int) -> Subject:
        if subject_id == required_subject_id:
            raise bad_request("Disciplina não pode ser pré-requisito dela mesma")
        self.subjects.get_or_404(subject_id)
        required = self.subjects.get_or_404(required_subject_id)
        if self.repo.get_link(subject_id, required_subject_id):
            raise conflict("Pré-requisito já cadastrado")
        if reaches(self.repo.edges(), required_subject_id, subject_id):
            raise bad_request("Pré-requisito criaria dependência circular")
        self.repo.save(SubjectPrerequisite(subject_id=subject_id, required_subject_id=required_subject_id))
        return required

    def remove(self, subject_id: int, required_subject_id: int) -> None:
        link = self.repo.get_link(subject_id, required_subject_id)
        if not link:
            raise not_found("Pré-requisito não encontrado")
        self.repo.delete(link)
