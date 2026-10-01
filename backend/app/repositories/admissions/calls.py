from __future__ import annotations

from app.models.admissions import AdmissionCall, AdmissionCallStatus
from app.repositories.academic._base import Repository


class AdmissionCallRepository(Repository[AdmissionCall]):
    model = AdmissionCall

    def list(self) -> list[AdmissionCall]:
        return self.db.query(AdmissionCall).order_by(AdmissionCall.opens_at.desc(), AdmissionCall.id.desc()).all()

    def list_published(self) -> list[AdmissionCall]:
        """Editais visiveis ao publico (tudo menos rascunho)."""
        return (
            self.db.query(AdmissionCall)
            .filter(AdmissionCall.status != AdmissionCallStatus.draft)
            .order_by(AdmissionCall.closes_at.desc(), AdmissionCall.id.desc())
            .all()
        )
