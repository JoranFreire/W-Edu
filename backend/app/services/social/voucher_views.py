"""Saida dos beneficios liberados (QR) para a equipe, o aluno e o responsavel."""

from __future__ import annotations

from datetime import date

from app.core import qr
from app.models.social_programs import BenefitVoucher
from app.schemas.academic_groups import PersonSummary
from app.schemas.benefit_vouchers import VoucherOut

QR_PREFIX = "wedu-beneficio:"


def qr_payload(code: str) -> str:
    return qr.qr_payload(QR_PREFIX, code)


def code_from_scan(value: str) -> str:
    """Aceita o conteudo lido do QR ou o codigo digitado."""
    return qr.code_from_scan(QR_PREFIX, value)


def voucher_out(voucher: BenefitVoucher, today: date | None = None) -> VoucherOut:
    status = "expired" if voucher.is_expired(today or date.today()) else voucher.status.value
    return VoucherOut(
        id=voucher.id, code=voucher.code, qr_payload=qr_payload(voucher.code), status=status,
        item_id=voucher.item_id, item_name=voucher.item.name, item_kind=voucher.item.kind, unit=voucher.item.unit,
        quantity=voucher.quantity, student=PersonSummary.model_validate(voucher.student),
        class_offering_id=voucher.class_offering_id, class_offering_name=voucher.class_offering.name,
        scheduled_meeting_id=voucher.scheduled_meeting_id, valid_until=voucher.valid_until,
        released_at=voucher.released_at, redeemed_at=voucher.redeemed_at,
    )
