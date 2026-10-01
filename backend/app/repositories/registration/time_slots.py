from __future__ import annotations
from uuid import UUID

from app.models.course_registration import OfferingTimeSlot
from app.repositories.academic._base import Repository


class OfferingTimeSlotRepository(Repository[OfferingTimeSlot]):
    model = OfferingTimeSlot

    def list_by_offering(self, offering_id: UUID) -> list[OfferingTimeSlot]:
        return self.by_offerings([offering_id]).get(offering_id, [])

    def by_offerings(self, offering_ids: list[UUID]) -> dict[UUID, list[OfferingTimeSlot]]:
        if not offering_ids:
            return {}
        rows = (
            self.db.query(OfferingTimeSlot)
            .filter(OfferingTimeSlot.class_offering_id.in_(offering_ids))
            .order_by(OfferingTimeSlot.weekday, OfferingTimeSlot.starts_at)
            .all()
        )
        grouped: dict[UUID, list[OfferingTimeSlot]] = {}
        for slot in rows:
            grouped.setdefault(slot.class_offering_id, []).append(slot)
        return grouped
