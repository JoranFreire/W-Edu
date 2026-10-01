from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.guardians import GuardianLinkRepository


class PayerResolver:
    """Responsavel financeiro do aluno (vinculo marcado como financeiro); sem ele, o proprio aluno paga."""

    def __init__(self, db: Session):
        self.links = GuardianLinkRepository(db)

    def payer_of(self, student_id: UUID) -> int | None:
        return next((link.guardian_id for link in self.links.list_by_student(student_id) if link.is_financial), None)
