from __future__ import annotations
from uuid import UUID

from app.models.assessment import GradingScheme
from app.models.schedule import ClassOffering
from app.repositories.academic._base import Repository


class GradingSchemeRepository(Repository[GradingScheme]):
    model = GradingScheme

    def list_all(self) -> list[GradingScheme]:
        return self.db.query(GradingScheme).order_by(GradingScheme.name).all()

    def get_by_name(self, name: str) -> GradingScheme | None:
        return self.db.query(GradingScheme).filter(GradingScheme.name == name).first()

    def get_default(self) -> GradingScheme | None:
        return self.db.query(GradingScheme).filter(GradingScheme.is_default.is_(True)).first()

    def clear_default(self, except_id: UUID | None = None) -> None:
        query = self.db.query(GradingScheme).filter(GradingScheme.is_default.is_(True))
        if except_id is not None:
            query = query.filter(GradingScheme.id != except_id)
        for scheme in query.all():
            scheme.is_default = False

    def is_used(self, scheme_id: UUID) -> bool:
        return self.db.query(ClassOffering.id).filter(ClassOffering.grading_scheme_id == scheme_id).first() is not None
