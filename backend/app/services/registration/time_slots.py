from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.course_registration import OfferingTimeSlot
from app.models.schedule import ClassOffering
from app.repositories.registration import OfferingTimeSlotRepository
from app.repositories.schedule import ClassOfferingRepository
from app.schemas.course_registration import TimeSlotCreate
from app.services.academic.errors import conflict, not_found
from app.services.registration.rules import WeeklySlot, overlaps


class OfferingTimeSlotService:
    """Horario semanal das ofertas, usado no choque de horario da matricula."""

    def __init__(self, db: Session):
        self.repo = OfferingTimeSlotRepository(db)
        self.offerings = ClassOfferingRepository(db)

    def list(self, offering_id: int) -> list[OfferingTimeSlot]:
        self._offering_or_404(offering_id)
        return self.repo.list_by_offering(offering_id)

    def add(self, offering_id: int, data: TimeSlotCreate) -> OfferingTimeSlot:
        self._offering_or_404(offering_id)
        new = WeeklySlot(data.weekday, data.starts_at, data.ends_at)
        if any(overlaps(new, WeeklySlot(s.weekday, s.starts_at, s.ends_at)) for s in self.repo.list_by_offering(offering_id)):
            raise conflict("Horário sobreposto a outro da mesma oferta")
        return self.repo.save(OfferingTimeSlot(class_offering_id=offering_id, **data.model_dump()))

    def remove(self, slot_id: int) -> None:
        slot = self.repo.get_by_id(slot_id)
        if not slot:
            raise not_found("Horário não encontrado")
        self.repo.delete(slot)

    def _offering_or_404(self, offering_id: int) -> ClassOffering:
        offering = self.offerings.get_by_id(offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        return offering
