from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_

from app.models.course_registration import RegistrationWindow
from app.repositories.academic._base import Repository


class RegistrationWindowRepository(Repository[RegistrationWindow]):
    model = RegistrationWindow

    def list(self, term_id: int | None = None) -> list[RegistrationWindow]:
        query = self.db.query(RegistrationWindow)
        if term_id is not None:
            query = query.filter(RegistrationWindow.term_id == term_id)
        return query.order_by(RegistrationWindow.opens_at.desc(), RegistrationWindow.id.desc()).all()

    def open_at(self, moment: datetime, program_ids: list[int]) -> list[RegistrationWindow]:
        """Janelas abertas no instante para algum dos programas (ou para todos)."""
        if not program_ids:
            return []
        return (
            self.db.query(RegistrationWindow)
            .filter(RegistrationWindow.opens_at <= moment, RegistrationWindow.closes_at > moment)
            .filter(or_(RegistrationWindow.program_id.is_(None), RegistrationWindow.program_id.in_(program_ids)))
            .order_by(RegistrationWindow.closes_at, RegistrationWindow.id)
            .all()
        )
