from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import Session

from app.models.schedule import ClassEnrollmentStatus, ClassOffering
from app.models.social_programs import BenefitDelivery, BenefitItem
from app.models.student import Student
from app.policies.retention_access import ensure_can_follow
from app.repositories.schedule import ClassOfferingRepository, ScheduledMeetingRepository
from app.repositories.social import BenefitDeliveryRepository, BenefitItemRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.social_programs import DeliveryOut, IndividualDeliveryInput, MeetingDeliveryInput, MeetingDeliveryOut
from app.services.academic.errors import conflict, not_found
from app.services.social.recipients import meeting_recipients
from app.services.social.stock import StockAvailability


def delivery_out(delivery: BenefitDelivery) -> DeliveryOut:
    return DeliveryOut(
        id=delivery.id, item_id=delivery.item_id, item_name=delivery.item.name, student=PersonSummary.model_validate(delivery.student),
        class_offering_id=delivery.class_offering_id, scheduled_meeting_id=delivery.scheduled_meeting_id,
        quantity=delivery.quantity, unit_cost_cents=delivery.unit_cost_cents, delivered_on=delivery.delivered_on,
    )


class BenefitDeliveryService:
    """Entregas de beneficios: em lote no encontro (lanche so para presentes) ou a um aluno; sempre com saldo em estoque."""

    def __init__(self, db: Session):
        self.db = db
        self.items = BenefitItemRepository(db)
        self.deliveries = BenefitDeliveryRepository(db)
        self.meetings = ScheduledMeetingRepository(db)
        self.offerings = ClassOfferingRepository(db)
        self.stock = StockAvailability(db)

    def deliver_in_meeting(self, meeting_id: UUID, data: MeetingDeliveryInput, user: Student) -> MeetingDeliveryOut:
        meeting = self.meetings.get_by_id(meeting_id)
        if not meeting:
            raise not_found("Encontro não encontrado")
        ensure_can_follow(user, meeting.class_offering)
        item = self._item(data.item_id)
        students = meeting_recipients(meeting, item, self.meetings)
        students -= self.deliveries.delivered_in_meeting(meeting.id, item.id)
        self.stock.ensure(item, len(students) * data.quantity)
        for student_id in sorted(students):
            self.db.add(BenefitDelivery(
                item_id=item.id, student_id=student_id, class_offering_id=meeting.class_offering_id, scheduled_meeting_id=meeting.id,
                quantity=data.quantity, unit_cost_cents=item.unit_cost_cents, delivered_on=meeting.starts_at.date(), delivered_by_id=user.id,
            ))
        self.db.commit()
        return MeetingDeliveryOut(delivered=len(students), remaining_stock=self.stock.available(item))

    def deliver_to_student(self, data: IndividualDeliveryInput, user: Student) -> DeliveryOut:
        offering = self._offering(data.class_offering_id)
        ensure_can_follow(user, offering)
        enrollment = self.offerings.get_enrollment(offering.id, data.student_id)
        if not enrollment or enrollment.status != ClassEnrollmentStatus.active:
            raise not_found("Aluno não inscrito nesta turma")
        item = self._item(data.item_id)
        self.stock.ensure(item, data.quantity)
        delivery = self.deliveries.save(BenefitDelivery(
            item_id=item.id, student_id=data.student_id, class_offering_id=offering.id, quantity=data.quantity,
            unit_cost_cents=item.unit_cost_cents, delivered_on=data.delivered_on or date.today(), delivered_by_id=user.id,
        ))
        return delivery_out(delivery)

    def list_for_offering(self, offering_id: UUID, user: Student) -> list[DeliveryOut]:
        ensure_can_follow(user, self._offering(offering_id))
        return [delivery_out(d) for d in self.deliveries.list_by_offering(offering_id)]

    def list_mine(self, user: Student) -> list[DeliveryOut]:
        return [delivery_out(d) for d in self.deliveries.list_by_student(user.id)]

    def _item(self, item_id: UUID) -> BenefitItem:
        item = self.items.lock(item_id)
        if not item:
            raise not_found("Item não encontrado")
        if not item.is_active:
            raise conflict("Item inativo")
        return item

    def _offering(self, offering_id: UUID) -> ClassOffering:
        offering = self.offerings.get_by_id(offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        return offering
