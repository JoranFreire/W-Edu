from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.social_programs import BenefitDelivery, BenefitVoucher, VoucherStatus
from app.models.student import Student
from app.repositories.social import BenefitItemRepository, BenefitVoucherRepository
from app.schemas.benefit_vouchers import VoucherOut
from app.services.academic.errors import conflict, not_found
from app.services.social.stock import StockAvailability
from app.services.social.voucher_views import code_from_scan, voucher_out

_REFUSALS = {
    VoucherStatus.redeemed: "Este benefício já foi retirado",
    VoucherStatus.cancelled: "Este benefício foi cancelado",
}


class VoucherRedemptionService:
    """Validacao do QR na retirada: confere (aluno, item, situacao) e confirma, gerando a entrega."""

    def __init__(self, db: Session):
        self.db = db
        self.items = BenefitItemRepository(db)
        self.vouchers = BenefitVoucherRepository(db)
        self.stock = StockAvailability(db)

    def lookup(self, scanned: str) -> VoucherOut:
        """So consulta: quem valida confere o nome do aluno antes de confirmar."""
        return voucher_out(self._voucher(scanned))

    def redeem(self, scanned: str, user: Student) -> VoucherOut:
        voucher = self._voucher(scanned, lock=True)
        today = date.today()
        if voucher.status in _REFUSALS:
            raise conflict(_REFUSALS[voucher.status])
        if voucher.is_expired(today):
            raise conflict("Este benefício venceu")
        item = self.items.lock(voucher.item_id)
        # A reserva deste QR ja estava descontada do disponivel: ela mesma cobre a retirada.
        self.stock.ensure(item, voucher.quantity, ignoring_reserved=voucher.quantity)
        delivery = BenefitDelivery(
            item_id=item.id, student_id=voucher.student_id, class_offering_id=voucher.class_offering_id,
            scheduled_meeting_id=voucher.scheduled_meeting_id, quantity=voucher.quantity, unit_cost_cents=item.unit_cost_cents,
            delivered_on=today, delivered_by_id=user.id,
        )
        self.db.add(delivery)
        self.db.flush()
        voucher.status = VoucherStatus.redeemed
        voucher.redeemed_at = datetime.now(timezone.utc)
        voucher.redeemed_by_id = user.id
        voucher.delivery_id = delivery.id
        return voucher_out(self.vouchers.save(voucher), today)

    def _voucher(self, scanned: str, *, lock: bool = False) -> BenefitVoucher:
        voucher = self.vouchers.get_by_code(code_from_scan(scanned), lock=lock)
        if not voucher:
            raise not_found("QR não reconhecido nesta instituição")
        return voucher
