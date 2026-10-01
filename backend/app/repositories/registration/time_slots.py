from __future__ import annotations

from app.models.course_registration import OfferingTimeSlot
from app.repositories.academic._base import Repository


class OfferingTimeSlotRepository(Repository[OfferingTimeSlot]):
    model = OfferingTimeSlot

    def list_by_offering(self, offering_id: int) -> list[OfferingTimeSlot]:
        return self.by_offerings([offering_id]).get(offering_id, [])

    def by_offerings(self, offering_ids: list[int]) -> dict[int, list[OfferingTimeSlot]]:
        if not offering_ids:
            return {}
        rows = (
            self.db.query(OfferingTimeSlot)
            .filter(OfferingTimeSlot.class_offering_id.in_(offering_ids))
            .order_by(OfferingTimeSlot.weekday, OfferingTimeSlot.starts_at)
            .all()
        )
        grouped: dict[int, list[OfferingTimeSlot]] = {}
        for slot in rows:
            grouped.setdefault(slot.class_offering_id, []).append(slot)
        return grouped
