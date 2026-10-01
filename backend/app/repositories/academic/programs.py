from __future__ import annotations
from uuid import UUID

from app.models.academic import Curriculum, Program, ProgramLevel, ProgramStatus
from app.repositories.academic._base import Repository


class ProgramRepository(Repository[Program]):
    model = Program

    def list(
        self,
        unit_id: UUID | None = None,
        level: ProgramLevel | None = None,
        status: ProgramStatus | None = None,
    ) -> list[Program]:
        query = self.db.query(Program)
        if unit_id is not None:
            query = query.filter(Program.unit_id == unit_id)
        if level is not None:
            query = query.filter(Program.level == level)
        if status is not None:
            query = query.filter(Program.status == status)
        return query.order_by(Program.name).all()

    def get_by_code(self, code: str) -> Program | None:
        return self.db.query(Program).filter(Program.code == code).first()

    def has_curricula(self, program_id: UUID) -> bool:
        return self.db.query(Curriculum.id).filter(Curriculum.program_id == program_id).first() is not None
