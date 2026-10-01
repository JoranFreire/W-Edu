from __future__ import annotations
from uuid import UUID

from app.models.schedule import ClassOffering
from app.models.social_programs import FundingSource
from app.repositories.academic._base import Repository


class FundingSourceRepository(Repository[FundingSource]):
    model = FundingSource

    def list(self) -> list[FundingSource]:
        return self.db.query(FundingSource).order_by(FundingSource.is_active.desc(), FundingSource.starts_on.desc(), FundingSource.id).all()

    def funded_offerings(self, funding_id: UUID) -> list[ClassOffering]:
        return (
            self.db.query(ClassOffering)
            .filter(ClassOffering.funding_source_id == funding_id)
            .order_by(ClassOffering.starts_at, ClassOffering.id)
            .all()
        )
