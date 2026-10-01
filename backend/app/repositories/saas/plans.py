from __future__ import annotations

from app.models.saas import SaasPlan
from app.repositories.academic._base import Repository


class SaasPlanRepository(Repository[SaasPlan]):
    model = SaasPlan

    def list(self) -> list[SaasPlan]:
        return self.db.query(SaasPlan).order_by(SaasPlan.monthly_price_cents, SaasPlan.id).all()

    def get_by_name(self, name: str) -> SaasPlan | None:
        return self.db.query(SaasPlan).filter(SaasPlan.name == name).first()
