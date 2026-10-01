from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.tenancy import bound_institution_id
from app.models.institution import Institution
from app.schemas.tuition import LateFeeSettings
from app.services.tuition.rules import LateFeePolicy

SETTINGS_KEY = "finance"


class LateFeeSettingsService:
    """Multa e juros de mora da instituicao, guardados em `institutions.settings["finance"]`."""

    def __init__(self, db: Session):
        self.db = db

    def get(self) -> LateFeeSettings:
        return LateFeeSettings(**(self._institution().settings or {}).get(SETTINGS_KEY, {}))

    def update(self, data: LateFeeSettings) -> LateFeeSettings:
        institution = self._institution()
        # Novo dicionario para o SQLAlchemy detectar a mudanca no JSON.
        institution.settings = {**(institution.settings or {}), SETTINGS_KEY: data.model_dump()}
        self.db.commit()
        return self.get()

    def policy(self) -> LateFeePolicy:
        current = self.get()
        return LateFeePolicy(fine_percent=current.fine_percent, monthly_interest_percent=current.monthly_interest_percent)

    def _institution(self) -> Institution:
        return self.db.get(Institution, bound_institution_id(self.db))
