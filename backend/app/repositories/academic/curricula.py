from uuid import UUID

from sqlalchemy.orm import joinedload

from app.models.academic import Curriculum, CurriculumComponent, CurriculumStatus
from app.repositories.academic._base import Repository


class CurriculumRepository(Repository[Curriculum]):
    model = Curriculum

    def list_by_program(self, program_id: UUID) -> list[Curriculum]:
        return self.db.query(Curriculum).filter(Curriculum.program_id == program_id).order_by(Curriculum.id).all()

    def get_with_components(self, curriculum_id: UUID) -> Curriculum | None:
        return (
            self.db.query(Curriculum)
            .options(joinedload(Curriculum.components).joinedload(CurriculumComponent.subject))
            .filter(Curriculum.id == curriculum_id)
            .first()
        )

    def get_version(self, program_id: UUID, version: str) -> Curriculum | None:
        return (
            self.db.query(Curriculum)
            .filter(Curriculum.program_id == program_id, Curriculum.version == version)
            .first()
        )

    def list_active(self, program_id: UUID) -> list[Curriculum]:
        return (
            self.db.query(Curriculum)
            .filter(Curriculum.program_id == program_id, Curriculum.status == CurriculumStatus.active)
            .all()
        )


class CurriculumComponentRepository(Repository[CurriculumComponent]):
    model = CurriculumComponent

    def get_by_subject(self, curriculum_id: UUID, subject_id: UUID) -> CurriculumComponent | None:
        return (
            self.db.query(CurriculumComponent)
            .filter(CurriculumComponent.curriculum_id == curriculum_id, CurriculumComponent.subject_id == subject_id)
            .first()
        )
