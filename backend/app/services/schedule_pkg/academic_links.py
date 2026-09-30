"""Vinculos academicos opcionais de uma oferta: periodo letivo, disciplina e turma-grupo."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.academic import AcademicTermRepository, ClassGroupRepository, SubjectRepository
from app.services.academic.errors import bad_request, not_found


@dataclass(frozen=True)
class AcademicLinks:
    term_id: int | None
    subject_id: int | None
    class_group_id: int | None


class OfferingAcademicLinks:
    def __init__(self, db: Session):
        self.terms = AcademicTermRepository(db)
        self.subjects = SubjectRepository(db)
        self.groups = ClassGroupRepository(db)

    def resolve(self, links: AcademicLinks) -> AcademicLinks:
        """Valida as referencias; a turma-grupo define o periodo quando ele nao vem informado."""
        term_id = links.term_id
        if links.class_group_id is not None:
            group = self.groups.get_by_id(links.class_group_id)
            if not group:
                raise not_found("Turma-grupo não encontrada")
            if term_id is not None and term_id != group.term_id:
                raise bad_request("A turma-grupo é de outro período letivo")
            term_id = group.term_id
        if term_id is not None and not self.terms.get_by_id(term_id):
            raise not_found("Período letivo não encontrado")
        if links.subject_id is not None and not self.subjects.get_by_id(links.subject_id):
            raise not_found("Disciplina não encontrada")
        return AcademicLinks(term_id=term_id, subject_id=links.subject_id, class_group_id=links.class_group_id)
