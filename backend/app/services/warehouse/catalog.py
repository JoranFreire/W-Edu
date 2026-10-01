from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.warehouse import WarehouseEntry, WarehouseItem
from app.repositories.warehouse import WarehouseEntryRepository, WarehouseItemRepository
from app.schemas.warehouse import EntryCreate, ItemCreate, ItemOut, ItemUpdate
from app.services.academic.errors import not_found
from app.services.academic.patch import apply_patch
from app.services.social.funding import FundingSourceService
from app.services.warehouse.rules import available


class WarehouseCatalogService:
    """Materiais do almoxarifado com saldo, emprestimos e alerta de estoque minimo; entradas de material."""

    def __init__(self, db: Session):
        self.items = WarehouseItemRepository(db)
        self.entries = WarehouseEntryRepository(db)
        self.funding = FundingSourceService(db)

    def list(self, only_active: bool = False) -> list[ItemOut]:
        items = [item for item in self.items.list() if item.is_active or not only_active]
        return self._out(items)

    def get_or_404(self, item_id: int) -> WarehouseItem:
        item = self.items.get_by_id(item_id)
        if not item:
            raise not_found("Material não encontrado")
        return item

    def create(self, data: ItemCreate) -> ItemOut:
        return self._out([self.items.save(WarehouseItem(**data.model_dump()))])[0]

    def update(self, item_id: int, data: ItemUpdate) -> ItemOut:
        item = self.get_or_404(item_id)
        apply_patch(item, data, clearable=frozenset({"category", "location"}))
        return self._out([self.items.save(item)])[0]

    def entries_of(self, item_id: int) -> list[WarehouseEntry]:
        self.get_or_404(item_id)
        return self.entries.list_by_item(item_id)

    def receive(self, item_id: int, data: EntryCreate, user: Student) -> ItemOut:
        item = self.get_or_404(item_id)
        if data.funding_source_id is not None:
            self.funding.get_or_404(data.funding_source_id)
        payload = data.model_dump()
        payload["unit_cost_cents"] = item.unit_cost_cents if data.unit_cost_cents is None else data.unit_cost_cents
        self.entries.save(WarehouseEntry(item_id=item.id, created_by_id=user.id, **payload))
        return self._out([item])[0]

    def balances(self, item_ids: list[int]) -> dict[int, int]:
        return {item_id: available(r, d, b) for item_id, (r, d, b, _) in self.items.movements(item_ids).items()}

    def _out(self, items: list[WarehouseItem]) -> list[ItemOut]:
        movements = self.items.movements([item.id for item in items])
        result = []
        for item in items:
            received, delivered, returned, lost = movements.get(item.id, (0, 0, 0, 0))
            stock = available(received, delivered, returned)
            result.append(ItemOut(
                id=item.id, name=item.name, category=item.category, kind=item.kind, unit=item.unit, min_stock=item.min_stock,
                location=item.location, unit_cost_cents=item.unit_cost_cents, is_active=item.is_active, available=stock,
                on_loan=max(delivered - returned - lost, 0) if item.kind.value == "durable" else 0, below_minimum=stock < item.min_stock,
            ))
        return result
