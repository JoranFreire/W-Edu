from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.tenancy import bound_institution_id
from app.repositories.integrations import MembershipEventRepository
from app.schemas.integrations import MembershipEventOut

MAX_PAGE = 500


class MembershipFeedService:
    """Fins de vinculo da instituicao ativa, em ordem, para o Persona revogar o acesso (catraca).

    O Persona consulta a partir do ultimo horario visto (`since`, inclusivo) e ignora ids repetidos.
    """

    def __init__(self, db: Session):
        self.db = db
        self.events = MembershipEventRepository(db)

    def since(self, since: datetime | None, limit: int) -> list[MembershipEventOut]:
        institution_id = bound_institution_id(self.db)
        rows = self.events.since(institution_id, since, min(max(limit, 1), MAX_PAGE)) if institution_id else []
        return [MembershipEventOut(id=row.id, user_id=row.user_id, kind=row.kind, occurred_at=row.created_at) for row in rows]
