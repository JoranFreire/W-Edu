from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.facial_login import FacialLoginAssertion


class FacialLoginAssertionRepository:
    def __init__(self, db: Session):
        self.db = db

    def consume(self, jti: str, user_id: UUID, expires_at: datetime) -> bool:
        """Registra o ``jti``; falso se ja tinha sido usado."""
        try:
            with self.db.begin_nested():
                self.db.add(FacialLoginAssertion(jti=jti, user_id=user_id, expires_at=expires_at))
        except IntegrityError:
            return False
        return True
