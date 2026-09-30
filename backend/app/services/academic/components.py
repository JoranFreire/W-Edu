from sqlalchemy.orm import Session

from app.models.academic import CurriculumComponent
from app.repositories.academic import CurriculumComponentRepository
from app.schemas.academic import CurriculumComponentCreate, CurriculumComponentUpdate
from app.services.academic.curricula import CurriculumService
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.subjects import SubjectService


class CurriculumComponentService:
    """Componentes so mudam em matrizes em rascunho."""

    def __init__(self, db: Session):
        self.repo = CurriculumComponentRepository(db)
        self.curricula = CurriculumService(db)
        self.subjects = SubjectService(db)

    def add(self, curriculum_id: int, data: CurriculumComponentCreate) -> CurriculumComponent:
        curriculum = self.curricula.get_draft_or_409(curriculum_id)
        subject = self.subjects.get_or_404(data.subject_id)
        if not subject.is_active:
            raise bad_request("Disciplina inativa não pode entrar na matriz")
        if self.repo.get_by_subject(curriculum.id, subject.id):
            raise conflict("Disciplina já está na matriz")
        return self.repo.save(CurriculumComponent(curriculum_id=curriculum.id, **data.model_dump()))

    def update(self, component_id: int, data: CurriculumComponentUpdate) -> CurriculumComponent:
        component = self._get_editable(component_id)
        apply_patch(component, data, clearable=frozenset({"hours", "credits"}))
        return self.repo.save(component)

    def remove(self, component_id: int) -> None:
        self.repo.delete(self._get_editable(component_id))

    def _get_editable(self, component_id: int) -> CurriculumComponent:
        component = self.repo.get_by_id(component_id)
        if not component:
            raise not_found("Componente não encontrado")
        self.curricula.get_draft_or_409(component.curriculum_id)
        return component
