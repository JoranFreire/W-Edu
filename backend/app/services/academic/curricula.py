from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic import Curriculum, CurriculumComponent, CurriculumStatus
from app.repositories.academic import CurriculumRepository, SubjectPrerequisiteRepository
from app.schemas.academic import CurriculumCreate, CurriculumDetail, CurriculumNewVersion, CurriculumUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.programs import ProgramService
from app.services.academic.review import curriculum_issues
from app.services.academic.summary import component_rows, totals


class CurriculumService:
    """Ciclo de vida da matriz: rascunho editavel -> ativa (uma por programa) -> arquivada."""

    def __init__(self, db: Session):
        self.repo = CurriculumRepository(db)
        self.prerequisites = SubjectPrerequisiteRepository(db)
        self.programs = ProgramService(db)

    def list_by_program(self, program_id: UUID) -> list[Curriculum]:
        self.programs.get_or_404(program_id)
        return self.repo.list_by_program(program_id)

    def get_or_404(self, curriculum_id: UUID) -> Curriculum:
        curriculum = self.repo.get_by_id(curriculum_id)
        if not curriculum:
            raise not_found("Matriz curricular não encontrada")
        return curriculum

    def get_draft_or_409(self, curriculum_id: UUID) -> Curriculum:
        curriculum = self.get_or_404(curriculum_id)
        if curriculum.status != CurriculumStatus.draft:
            raise conflict("Só matrizes em rascunho podem ser alteradas; crie uma nova versão")
        return curriculum

    def detail(self, curriculum_id: UUID) -> CurriculumDetail:
        curriculum = self.repo.get_with_components(curriculum_id)
        if not curriculum:
            raise not_found("Matriz curricular não encontrada")
        subject_ids = [component.subject_id for component in curriculum.components]
        edges = self.prerequisites.edges_for(subject_ids) if subject_ids else []
        return CurriculumDetail(
            id=curriculum.id,
            program_id=curriculum.program_id,
            version=curriculum.version,
            valid_from=curriculum.valid_from,
            status=curriculum.status,
            notes=curriculum.notes,
            components=component_rows(curriculum),
            totals=totals(curriculum),
            issues=curriculum_issues(curriculum, edges),
        )

    def create(self, program_id: UUID, data: CurriculumCreate) -> Curriculum:
        self.programs.get_or_404(program_id)
        self._ensure_unique_version(program_id, data.version)
        return self.repo.save(Curriculum(program_id=program_id, **data.model_dump()))

    def update(self, curriculum_id: UUID, data: CurriculumUpdate) -> Curriculum:
        curriculum = self.get_draft_or_409(curriculum_id)
        if data.version is not None and data.version != curriculum.version:
            self._ensure_unique_version(curriculum.program_id, data.version)
        apply_patch(curriculum, data, clearable=frozenset({"valid_from", "notes"}))
        return self.repo.save(curriculum)

    def delete(self, curriculum_id: UUID) -> None:
        self.repo.delete(self.get_draft_or_409(curriculum_id))

    def activate(self, curriculum_id: UUID) -> Curriculum:
        curriculum = self.get_draft_or_409(curriculum_id)
        if not curriculum.components:
            raise bad_request("Matriz sem componentes não pode ser ativada")
        for current in self.repo.list_active(curriculum.program_id):
            current.status = CurriculumStatus.archived
        curriculum.status = CurriculumStatus.active
        return self.repo.save(curriculum)

    def archive(self, curriculum_id: UUID) -> Curriculum:
        curriculum = self.get_or_404(curriculum_id)
        if curriculum.status != CurriculumStatus.active:
            raise conflict("Só a matriz ativa pode ser arquivada")
        curriculum.status = CurriculumStatus.archived
        return self.repo.save(curriculum)

    def new_version(self, curriculum_id: UUID, data: CurriculumNewVersion) -> Curriculum:
        """Copia os componentes para um novo rascunho; a origem fica intacta."""
        source = self.get_or_404(curriculum_id)
        self._ensure_unique_version(source.program_id, data.version)
        draft = Curriculum(program_id=source.program_id, version=data.version, valid_from=data.valid_from, notes=source.notes)
        draft.components = [
            CurriculumComponent(
                subject_id=component.subject_id,
                term_number=component.term_number,
                kind=component.kind,
                hours=component.hours,
                credits=component.credits,
            )
            for component in source.components
        ]
        return self.repo.save(draft)

    def _ensure_unique_version(self, program_id: UUID, version: str) -> None:
        if self.repo.get_version(program_id, version):
            raise conflict("Versão já existe para este programa")
