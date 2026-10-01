from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic import AcademicUnit
from app.repositories.academic import AcademicUnitRepository
from app.schemas.academic import AcademicUnitCreate, AcademicUnitUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.graph import reaches
from app.services.academic.patch import apply_patch


class AcademicUnitService:
    def __init__(self, db: Session):
        self.repo = AcademicUnitRepository(db)

    def list(self) -> list[AcademicUnit]:
        return self.repo.list_all()

    def get_or_404(self, unit_id: UUID) -> AcademicUnit:
        unit = self.repo.get_by_id(unit_id)
        if not unit:
            raise not_found("Unidade acadêmica não encontrada")
        return unit

    def create(self, data: AcademicUnitCreate) -> AcademicUnit:
        if data.parent_id is not None:
            self.get_or_404(data.parent_id)
        return self.repo.save(AcademicUnit(**data.model_dump()))

    def update(self, unit_id: UUID, data: AcademicUnitUpdate) -> AcademicUnit:
        unit = self.get_or_404(unit_id)
        if data.parent_id is not None:
            self._ensure_valid_parent(unit_id, data.parent_id)
        apply_patch(unit, data, clearable=frozenset({"parent_id"}))
        return self.repo.save(unit)

    def delete(self, unit_id: UUID) -> None:
        unit = self.get_or_404(unit_id)
        if self.repo.has_children(unit_id):
            raise conflict("Unidade possui subunidades")
        if self.repo.has_programs(unit_id):
            raise conflict("Unidade possui programas vinculados")
        self.repo.delete(unit)

    def _ensure_valid_parent(self, unit_id: UUID, parent_id: UUID) -> None:
        self.get_or_404(parent_id)
        # Aresta filho -> pai: o novo pai nao pode descender da propria unidade.
        edges = [(child, parent) for child, parent in self.repo.parent_map().items() if parent is not None]
        if parent_id == unit_id or reaches(edges, parent_id, unit_id):
            raise bad_request("Unidade não pode ficar abaixo dela mesma")
