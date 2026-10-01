from __future__ import annotations
from uuid import UUID

from app.models.secretariat import ProgramEnrollmentEvent
from app.repositories.academic._base import Repository


class EnrollmentEventRepository(Repository[ProgramEnrollmentEvent]):
    model = ProgramEnrollmentEvent

    def list_by_enrollment(self, enrollment_id: UUID) -> list[ProgramEnrollmentEvent]:
        return (
            self.db.query(ProgramEnrollmentEvent)
            .filter(ProgramEnrollmentEvent.program_enrollment_id == enrollment_id)
            .order_by(ProgramEnrollmentEvent.created_at, ProgramEnrollmentEvent.id)
            .all()
        )
