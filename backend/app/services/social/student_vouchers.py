from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import Session

from app.repositories.social import BenefitVoucherRepository
from app.schemas.benefit_vouchers import VoucherOut
from app.services.social.voucher_views import voucher_out


class StudentVoucherService:
    """Beneficios liberados de um aluno (o QR que ele mostra na retirada) e o historico."""

    def __init__(self, db: Session):
        self.vouchers = BenefitVoucherRepository(db)

    def for_student(self, student_id: UUID) -> list[VoucherOut]:
        today = date.today()
        return [voucher_out(voucher, today) for voucher in self.vouchers.list_by_student(student_id)]
