from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic import Program, ProgramLevel, ProgramStatus
from app.repositories.academic import ProgramRepository
from app.schemas.academic import ProgramCreate, ProgramUpdate
from app.services.academic.errors import conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.units import AcademicUnitService

CLEARABLE = frozenset({"unit_id", "degree", "duration_terms", "total_hours", "total_credits", "complementary_hours", "internship_hours"})


class ProgramService:
    def __init__(self, db: Session):
        self.repo = ProgramRepository(db)
        self.units = AcademicUnitService(db)

    def list(
        self,
        unit_id: UUID | None = None,
        level: ProgramLevel | None = None,
        status: ProgramStatus | None = None,
    ) -> list[Program]:
        return self.repo.list(unit_id=unit_id, level=level, status=status)

    def get_or_404(self, program_id: UUID) -> Program:
        program = self.repo.get_by_id(program_id)
        if not program:
            raise not_found("Programa não encontrado")
        return program

    def create(self, data: ProgramCreate) -> Program:
        if data.unit_id is not None:
            self.units.get_or_404(data.unit_id)
        self._ensure_unique_code(data.code)
        return self.repo.save(Program(**data.model_dump()))

    def update(self, program_id: UUID, data: ProgramUpdate) -> Program:
        program = self.get_or_404(program_id)
        if data.unit_id is not None:
            self.units.get_or_404(data.unit_id)
        if data.code is not None and data.code != program.code:
            self._ensure_unique_code(data.code)
        apply_patch(program, data, clearable=CLEARABLE)
        return self.repo.save(program)

    def delete(self, program_id: UUID) -> None:
        program = self.get_or_404(program_id)
        if self.repo.has_curricula(program_id):
            raise conflict("Programa possui matrizes curriculares")
        self.repo.delete(program)

    def _ensure_unique_code(self, code: str) -> None:
        if self.repo.get_by_code(code):
            raise conflict("Já existe programa com este código")
