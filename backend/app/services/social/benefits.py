from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.social_programs import BenefitItem, BenefitStockEntry
from app.models.student import Student
from app.repositories.social import BenefitItemRepository, BenefitStockRepository
from app.schemas.social_programs import BenefitItemCreate, BenefitItemOut, BenefitItemUpdate, StockEntryCreate
from app.services.academic.errors import not_found
from app.services.academic.patch import apply_patch
from app.services.social.funding import FundingSourceService


def item_out(item: BenefitItem, stock: int) -> BenefitItemOut:
    return BenefitItemOut(
        id=item.id, name=item.name, kind=item.kind, unit=item.unit, unit_cost_cents=item.unit_cost_cents,
        requires_attendance=item.requires_attendance, is_active=item.is_active, stock=stock,
    )


class BenefitCatalogService:
    """Itens de beneficio e entradas de estoque (compra ou doacao, com financiador)."""

    def __init__(self, db: Session):
        self.items = BenefitItemRepository(db)
        self.stock = BenefitStockRepository(db)
        self.funding = FundingSourceService(db)

    def list(self) -> list[BenefitItemOut]:
        items = self.items.list()
        balances = self.items.balances([item.id for item in items])
        return [item_out(item, balances.get(item.id, 0)) for item in items]

    def get_or_404(self, item_id: UUID) -> BenefitItem:
        item = self.items.get_by_id(item_id)
        if not item:
            raise not_found("Item não encontrado")
        return item

    def create(self, data: BenefitItemCreate) -> BenefitItemOut:
        return item_out(self.items.save(BenefitItem(**data.model_dump())), 0)

    def update(self, item_id: UUID, data: BenefitItemUpdate) -> BenefitItemOut:
        item = self.get_or_404(item_id)
        apply_patch(item, data)
        saved = self.items.save(item)
        return item_out(saved, self.items.balances([saved.id])[saved.id])

    def entries(self, item_id: UUID) -> list[BenefitStockEntry]:
        self.get_or_404(item_id)
        return self.stock.list_by_item(item_id)

    def receive(self, item_id: UUID, data: StockEntryCreate, user: Student) -> BenefitItemOut:
        item = self.get_or_404(item_id)
        if data.funding_source_id is not None:
            self.funding.get_or_404(data.funding_source_id)
        payload = data.model_dump()
        payload["unit_cost_cents"] = item.unit_cost_cents if data.unit_cost_cents is None else data.unit_cost_cents
        self.stock.save(BenefitStockEntry(item_id=item.id, created_by_id=user.id, **payload))
        return item_out(item, self.items.balances([item.id])[item.id])
