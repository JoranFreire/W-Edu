from __future__ import annotations

from app.models.contracts import ContractTemplate
from app.repositories.academic._base import Repository


class ContractTemplateRepository(Repository[ContractTemplate]):
    model = ContractTemplate

    def list(self) -> list[ContractTemplate]:
        return self.db.query(ContractTemplate).order_by(ContractTemplate.kind, ContractTemplate.name).all()
