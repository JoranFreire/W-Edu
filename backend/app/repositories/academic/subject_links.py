from sqlalchemy import or_

from app.models.academic import Subject, SubjectEquivalence, SubjectPrerequisite
from app.repositories.academic._base import Repository


class SubjectPrerequisiteRepository(Repository[SubjectPrerequisite]):
    model = SubjectPrerequisite

    def get_link(self, subject_id: int, required_subject_id: int) -> SubjectPrerequisite | None:
        return (
            self.db.query(SubjectPrerequisite)
            .filter(
                SubjectPrerequisite.subject_id == subject_id,
                SubjectPrerequisite.required_subject_id == required_subject_id,
            )
            .first()
        )

    def list_required(self, subject_id: int) -> list[Subject]:
        return (
            self.db.query(Subject)
            .join(SubjectPrerequisite, SubjectPrerequisite.required_subject_id == Subject.id)
            .filter(SubjectPrerequisite.subject_id == subject_id)
            .order_by(Subject.code)
            .all()
        )

    def edges(self) -> list[tuple[int, int]]:
        """Pares (disciplina, pre-requisito) da instituicao, para checar ciclos."""
        return self.db.query(SubjectPrerequisite.subject_id, SubjectPrerequisite.required_subject_id).all()

    def required_names(self, subject_ids: set[int]) -> dict[int, dict[int, str]]:
        """Pre-requisitos de cada disciplina, com o nome de cada exigida."""
        if not subject_ids:
            return {}
        rows = (
            self.db.query(SubjectPrerequisite.subject_id, Subject.id, Subject.name)
            .join(Subject, Subject.id == SubjectPrerequisite.required_subject_id)
            .filter(SubjectPrerequisite.subject_id.in_(subject_ids))
            .all()
        )
        required: dict[int, dict[int, str]] = {}
        for subject_id, required_id, name in rows:
            required.setdefault(subject_id, {})[required_id] = name
        return required

    def edges_for(self, subject_ids: list[int]) -> list[tuple[int, int]]:
        return (
            self.db.query(SubjectPrerequisite.subject_id, SubjectPrerequisite.required_subject_id)
            .filter(SubjectPrerequisite.subject_id.in_(subject_ids))
            .all()
        )


class SubjectEquivalenceRepository(Repository[SubjectEquivalence]):
    model = SubjectEquivalence

    def get_link(self, first_id: int, second_id: int) -> SubjectEquivalence | None:
        low, high = sorted((first_id, second_id))
        return (
            self.db.query(SubjectEquivalence)
            .filter(SubjectEquivalence.subject_id == low, SubjectEquivalence.equivalent_subject_id == high)
            .first()
        )

    def list_equivalents(self, subject_id: int) -> list[Subject]:
        links = (
            self.db.query(SubjectEquivalence)
            .filter(or_(SubjectEquivalence.subject_id == subject_id, SubjectEquivalence.equivalent_subject_id == subject_id))
            .all()
        )
        other_ids = [link.equivalent_subject_id if link.subject_id == subject_id else link.subject_id for link in links]
        if not other_ids:
            return []
        return self.db.query(Subject).filter(Subject.id.in_(other_ids)).order_by(Subject.code).all()
