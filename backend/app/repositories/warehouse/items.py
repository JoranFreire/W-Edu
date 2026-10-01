from __future__ import annotations
from uuid import UUID

from sqlalchemy import func

from app.models.warehouse import MaterialRequestLine, WarehouseEntry, WarehouseItem
from app.repositories.academic._base import Repository


class WarehouseItemRepository(Repository[WarehouseItem]):
    model = WarehouseItem

    def list(self) -> list[WarehouseItem]:
        return self.db.query(WarehouseItem).order_by(WarehouseItem.is_active.desc(), WarehouseItem.category, WarehouseItem.name).all()

    def lock_many(self, item_ids: list[UUID]) -> dict[UUID, WarehouseItem]:
        """Trava os itens durante a retirada (duas retiradas disputando o mesmo saldo)."""
        rows = self.db.query(WarehouseItem).filter(WarehouseItem.id.in_(item_ids)).with_for_update().all()
        return {item.id: item for item in rows}

    def movements(self, item_ids: list[UUID]) -> dict[UUID, tuple[int, int, int, int]]:
        """(recebido, entregue, devolvido, perdido) por item."""
        if not item_ids:
            return {}
        received = dict(
            self.db.query(WarehouseEntry.item_id, func.sum(WarehouseEntry.quantity))
            .filter(WarehouseEntry.item_id.in_(item_ids)).group_by(WarehouseEntry.item_id).all()
        )
        moved = {
            item_id: (int(d or 0), int(r or 0), int(l or 0))
            for item_id, d, r, l in self.db.query(
                MaterialRequestLine.item_id, func.sum(MaterialRequestLine.quantity_delivered),
                func.sum(MaterialRequestLine.quantity_returned), func.sum(MaterialRequestLine.quantity_lost),
            ).filter(MaterialRequestLine.item_id.in_(item_ids)).group_by(MaterialRequestLine.item_id).all()
        }
        return {item_id: (int(received.get(item_id) or 0), *moved.get(item_id, (0, 0, 0))) for item_id in item_ids}


class WarehouseEntryRepository(Repository[WarehouseEntry]):
    model = WarehouseEntry

    def list_by_item(self, item_id: UUID) -> list[WarehouseEntry]:
        return (
            self.db.query(WarehouseEntry)
            .filter(WarehouseEntry.item_id == item_id)
            .order_by(WarehouseEntry.received_on.desc(), WarehouseEntry.id.desc())
            .all()
        )
