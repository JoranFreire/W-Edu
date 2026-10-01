from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.social_programs import FundingSource
from app.repositories.social import FundingSourceRepository
from app.schemas.social_programs import FundingSourceCreate, FundingSourceUpdate
from app.services.academic.errors import bad_request, not_found
from app.services.academic.patch import apply_patch


class FundingSourceService:
    """Financiadores (convenio, governo, Sistema S, emenda, doacao, recursos proprios)."""

    def __init__(self, db: Session):
        self.repo = FundingSourceRepository(db)

    def list(self) -> list[FundingSource]:
        return self.repo.list()

    def get_or_404(self, funding_id: UUID) -> FundingSource:
        funding = self.repo.get_by_id(funding_id)
        if not funding:
            raise not_found("Financiador não encontrado")
        return funding

    def create(self, data: FundingSourceCreate) -> FundingSource:
        funding = FundingSource(**data.model_dump())
        self._validate(funding)
        return self.repo.save(funding)

    def update(self, funding_id: UUID, data: FundingSourceUpdate) -> FundingSource:
        funding = self.get_or_404(funding_id)
        apply_patch(funding, data, clearable=frozenset({"agreement_number", "amount_cents", "ends_on", "notes"}))
        self._validate(funding)
        return self.repo.save(funding)

    @staticmethod
    def _validate(funding: FundingSource) -> None:
        if funding.ends_on and funding.ends_on < funding.starts_on:
            raise bad_request("O fim da vigência não pode ser anterior ao início")
