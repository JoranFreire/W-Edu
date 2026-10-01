from __future__ import annotations

from datetime import date

from app.models.saas import PlatformInvoice
from app.repositories.academic._base import Repository


class PlatformInvoiceRepository(Repository[PlatformInvoice]):
    model = PlatformInvoice

    def list_for(self, institution_id: int) -> list[PlatformInvoice]:
        return (
            self.db.query(PlatformInvoice)
            .filter(PlatformInvoice.institution_id == institution_id)
            .order_by(PlatformInvoice.period_start.desc())
            .all()
        )

    def get_period(self, subscription_id: int, period_start: date) -> PlatformInvoice | None:
        return (
            self.db.query(PlatformInvoice)
            .filter(PlatformInvoice.subscription_id == subscription_id, PlatformInvoice.period_start == period_start)
            .first()
        )
