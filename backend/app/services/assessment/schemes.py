from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.assessment import GradingScheme
from app.models.schedule import ClassOffering
from app.repositories.assessment import GradingSchemeRepository
from app.schemas.assessment import GradingSchemeCreate, GradingSchemeOut, GradingSchemeUpdate
from app.services.academic.patch import apply_patch
from app.services.assessment.errors import bad_request, conflict, not_found

# Usado quando a instituicao ainda nao cadastrou esquema (0 a 10, media 6, 75% de frequencia).
FALLBACK_SCHEME = GradingSchemeOut(
    id=None, name="Padrão (0 a 10)", scale="numeric", min_value=0, max_value=10, passing_grade=6,
    formula="weighted", recovery_enabled=True, min_attendance=75, concepts=[], is_default=True,
)


class GradingSchemeService:
    def __init__(self, db: Session):
        self.repo = GradingSchemeRepository(db)

    def list(self) -> list[GradingScheme]:
        return self.repo.list_all()

    def get_or_404(self, scheme_id: int) -> GradingScheme:
        scheme = self.repo.get_by_id(scheme_id)
        if not scheme:
            raise not_found("Esquema de avaliação não encontrado")
        return scheme

    def effective_for(self, offering: ClassOffering) -> GradingSchemeOut:
        """Esquema da oferta, senao o padrao da instituicao, senao o embutido."""
        scheme = self.repo.get_by_id(offering.grading_scheme_id) if offering.grading_scheme_id else self.repo.get_default()
        return GradingSchemeOut.model_validate(scheme) if scheme else FALLBACK_SCHEME

    def create(self, data: GradingSchemeCreate) -> GradingScheme:
        if self.repo.get_by_name(data.name):
            raise conflict("Já existe esquema com este nome")
        if data.is_default:
            self.repo.clear_default()
        return self.repo.save(GradingScheme(**data.model_dump()))

    def update(self, scheme_id: int, data: GradingSchemeUpdate) -> GradingScheme:
        scheme = self.get_or_404(scheme_id)
        if data.name is not None and data.name != scheme.name and self.repo.get_by_name(data.name):
            raise conflict("Já existe esquema com este nome")
        apply_patch(scheme, data)
        if data.concepts is not None:
            scheme.concepts = [band.model_dump() for band in data.concepts]
        if scheme.max_value <= scheme.min_value or not scheme.min_value <= scheme.passing_grade <= scheme.max_value:
            raise bad_request("Escala ou média de aprovação inválida")
        if data.is_default:
            self.repo.clear_default(except_id=scheme.id)
        return self.repo.save(scheme)

    def delete(self, scheme_id: int) -> None:
        scheme = self.get_or_404(scheme_id)
        if self.repo.is_used(scheme_id):
            raise conflict("Esquema em uso por turmas")
        self.repo.delete(scheme)
