from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.guardians import GuardianLinkRepository


class FamilyRecipients:
    """Destinatarios de um comunicado a familia: o proprio aluno e os responsaveis vinculados a ele."""

    def __init__(self, db: Session):
        self.links = GuardianLinkRepository(db)

    def of(self, student_id: int) -> list[int]:
        return self.of_many([student_id])

    def of_many(self, student_ids: list[int]) -> list[int]:
        """Sem repeticao: o responsavel de dois irmaos da mesma turma recebe um aviso so."""
        guardians = self.links.guardian_ids_of(student_ids)
        return list(dict.fromkeys([*student_ids, *guardians]))
