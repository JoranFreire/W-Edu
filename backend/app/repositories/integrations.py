from __future__ import annotations
from uuid import UUID

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.gate_passage import GatePassage
from app.models.institution import InstitutionMembership
from app.models.membership_event import MembershipEvent


class GatePassageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_once(self, passage: GatePassage) -> bool:
        """Grava a passagem; falso se o mesmo aviso (``jti``) ja tinha chegado."""
        if self.db.execute(select(GatePassage.id).where(GatePassage.jti == passage.jti)).first():
            return False
        try:
            with self.db.begin_nested():
                self.db.add(passage)
        except IntegrityError:
            return False
        return True


class MembershipEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def since(self, institution_id: UUID, since: datetime | None, limit: int) -> list[MembershipEvent]:
        query = select(MembershipEvent).where(MembershipEvent.institution_id == institution_id)
        if since is not None:
            query = query.where(MembershipEvent.created_at >= since)
        return list(self.db.scalars(query.order_by(MembershipEvent.created_at, MembershipEvent.id).limit(limit)))


class ActiveMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_active_member(self, institution_id: UUID, user_id: UUID) -> bool:
        return self.db.execute(
            select(InstitutionMembership.id).where(
                InstitutionMembership.institution_id == institution_id,
                InstitutionMembership.user_id == user_id,
                InstitutionMembership.is_active.is_(True),
            )
        ).first() is not None
