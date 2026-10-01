from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.social_programs import BenefitItem
from app.repositories.social import BenefitItemRepository, BenefitVoucherRepository
from app.services.academic.errors import conflict


class StockAvailability:
    """Saldo disponivel: estoque fisico menos o que ja esta liberado em QR e ainda nao foi retirado."""

    def __init__(self, db: Session):
        self.items = BenefitItemRepository(db)
        self.vouchers = BenefitVoucherRepository(db)

    def available(self, item: BenefitItem, *, ignoring_reserved: int = 0) -> int:
        """`ignoring_reserved`: parte da reserva que esta sendo consumida agora (a do QR validado)."""
        balance = self.items.balances([item.id])[item.id]
        reserved = self.vouchers.reserved([item.id], date.today())[item.id]
        return balance - reserved + ignoring_reserved

    def ensure(self, item: BenefitItem, needed: int, *, ignoring_reserved: int = 0) -> None:
        available = self.available(item, ignoring_reserved=ignoring_reserved)
        if needed > available:
            raise conflict(f"Estoque insuficiente de {item.name}: {available} disponível(is), {needed} necessário(s)")
