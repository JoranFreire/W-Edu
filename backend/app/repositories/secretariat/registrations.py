from __future__ import annotations

from app.models.secretariat import TermRegistration
from app.repositories.academic._base import Repository


class TermRegistrationRepository(Repository[TermRegistration]):
    model = TermRegistration

    def list_by_enrollment(self, enrollment_id: int) -> list[TermRegistration]:
        return (
            self.db.query(TermRegistration)
            .filter(TermRegistration.program_enrollment_id == enrollment_id)
            .order_by(TermRegistration.registered_at)
            .all()
        )

    def get(self, enrollment_id: int, term_id: int) -> TermRegistration | None:
        return (
            self.db.query(TermRegistration)
            .filter(TermRegistration.program_enrollment_id == enrollment_id, TermRegistration.term_id == term_id)
            .first()
        )
