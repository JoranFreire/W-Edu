from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import Session

from app.core.signing import validation_code
from app.models.schedule import ClassEnrollmentStatus, ClassOffering
from app.models.social_programs import BenefitItem, BenefitVoucher, VoucherStatus
from app.models.student import Student
from app.policies.retention_access import ensure_can_follow
from app.repositories.schedule import ClassOfferingRepository, ScheduledMeetingRepository
from app.repositories.social import BenefitDeliveryRepository, BenefitItemRepository, BenefitVoucherRepository
from app.schemas.benefit_vouchers import IndividualVoucherInput, MeetingVoucherInput, MeetingVoucherOut, VoucherOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.social.recipients import meeting_recipients
from app.services.social.stock import StockAvailability
from app.services.social.voucher_views import voucher_out


class VoucherReleaseService:
    """Libera beneficios para retirada com QR (no encontro ou a um aluno), reservando o estoque; e os cancela."""

    def __init__(self, db: Session):
        self.db = db
        self.items = BenefitItemRepository(db)
        self.vouchers = BenefitVoucherRepository(db)
        self.deliveries = BenefitDeliveryRepository(db)
        self.meetings = ScheduledMeetingRepository(db)
        self.offerings = ClassOfferingRepository(db)
        self.stock = StockAvailability(db)

    def release_in_meeting(self, meeting_id: UUID, data: MeetingVoucherInput, user: Student) -> MeetingVoucherOut:
        meeting = self.meetings.get_by_id(meeting_id)
        if not meeting:
            raise not_found("Encontro não encontrado")
        ensure_can_follow(user, meeting.class_offering)
        item = self._item(data.item_id)
        self._ensure_valid_until(data.valid_until)
        students = meeting_recipients(meeting, item, self.meetings)
        # Quem ja tem o item liberado ou ja o recebeu neste encontro fica de fora.
        students -= self.vouchers.pending_students(meeting.class_offering_id, item.id, meeting.id, date.today())
        students -= self.deliveries.delivered_in_meeting(meeting.id, item.id)
        self.stock.ensure(item, len(students) * data.quantity)
        for student_id in sorted(students):
            self.db.add(self._voucher(item, student_id, meeting.class_offering_id, data.quantity, data.valid_until, user, meeting.id))
        self.db.commit()
        return MeetingVoucherOut(released=len(students), available_stock=self.stock.available(item))

    def release_to_student(self, data: IndividualVoucherInput, user: Student) -> VoucherOut:
        offering = self._offering(data.class_offering_id)
        ensure_can_follow(user, offering)
        enrollment = self.offerings.get_enrollment(offering.id, data.student_id)
        if not enrollment or enrollment.status != ClassEnrollmentStatus.active:
            raise not_found("Aluno não inscrito nesta turma")
        item = self._item(data.item_id)
        self._ensure_valid_until(data.valid_until)
        self.stock.ensure(item, data.quantity)
        voucher = self.vouchers.save(self._voucher(item, data.student_id, offering.id, data.quantity, data.valid_until, user))
        return voucher_out(voucher)

    def list_for_offering(self, offering_id: UUID, user: Student) -> list[VoucherOut]:
        ensure_can_follow(user, self._offering(offering_id))
        today = date.today()
        return [voucher_out(voucher, today) for voucher in self.vouchers.list_by_offering(offering_id)]

    def cancel(self, voucher_id: UUID, user: Student) -> VoucherOut:
        voucher = self.vouchers.get_by_id(voucher_id)
        if not voucher:
            raise not_found("Benefício não encontrado")
        ensure_can_follow(user, voucher.class_offering)
        if voucher.status != VoucherStatus.released:
            raise conflict("Só é possível cancelar benefício ainda não retirado")
        voucher.status = VoucherStatus.cancelled
        return voucher_out(self.vouchers.save(voucher))

    def _voucher(
        self, item: BenefitItem, student_id: UUID, offering_id: UUID, quantity: int, valid_until: date | None,
        user: Student, meeting_id: UUID | None = None,
    ) -> BenefitVoucher:
        return BenefitVoucher(
            code=validation_code(), item_id=item.id, student_id=student_id, class_offering_id=offering_id,
            scheduled_meeting_id=meeting_id, quantity=quantity, valid_until=valid_until, released_by_id=user.id,
        )

    @staticmethod
    def _ensure_valid_until(valid_until: date | None) -> None:
        if valid_until is not None and valid_until < date.today():
            raise bad_request("A validade não pode ser no passado")

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
