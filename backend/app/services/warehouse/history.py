from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.warehouse import MaterialRequestRepository, MaterialReturnRepository, WarehouseEntryRepository
from app.schemas.warehouse import MovementOut
from app.services.warehouse.catalog import WarehouseCatalogService


class WarehouseHistoryService:
    """Extrato do material: entradas, retiradas (com quem retirou e como), devolucoes e perdas, do mais recente ao mais antigo."""

    def __init__(self, db: Session):
        self.catalog = WarehouseCatalogService(db)
        self.entries = WarehouseEntryRepository(db)
        self.requests = MaterialRequestRepository(db)
        self.returns = MaterialReturnRepository(db)

    def of_item(self, item_id: UUID) -> list[MovementOut]:
        self.catalog.get_or_404(item_id)
        movements = [*self._entries(item_id), *self._deliveries(item_id), *self._returns(item_id)]
        return sorted(movements, key=lambda movement: movement.occurred_at, reverse=True)

    def _entries(self, item_id: UUID) -> list[MovementOut]:
        return [
            MovementOut(
                occurred_at=entry.created_at, kind="entry",
                quantity=entry.quantity, person=None, detail=f"{'Doação' if entry.origin.value == 'donation' else 'Compra'}"
                + (f" · {entry.notes}" if entry.notes else ""),
            )
            for entry in self.entries.list_by_item(item_id)
        ]

    def _deliveries(self, item_id: UUID) -> list[MovementOut]:
        result = []
        for line in self.requests.delivered_lines_of_item(item_id):
            request = line.request
            operator = f" · entregue por {request.delivered_by.name}" if request.delivered_by else ""
            note = f" · {request.delivery_note}" if request.delivery_note else ""
            result.append(MovementOut(
                occurred_at=request.delivered_at, kind="delivery", quantity=line.quantity_delivered, person=request.requester.name,
                detail=f"{request.purpose}{operator}{note}", request_id=request.id, method=request.delivery_method,
            ))
        return result

    def _returns(self, item_id: UUID) -> list[MovementOut]:
        result = []
        for event in self.returns.list_by_item(item_id):
            receiver = f"recebido por {event.received_by.name}" if event.received_by else None
            detail = " · ".join(part for part in (receiver, event.note) if part) or None
            person = event.request.requester.name
            if event.returned:
                result.append(MovementOut(occurred_at=event.created_at, kind="return", quantity=event.returned, person=person,
                                          detail=detail, request_id=event.request_id))
            if event.lost:
                result.append(MovementOut(occurred_at=event.created_at, kind="loss", quantity=event.lost, person=person,
                                          detail=detail, request_id=event.request_id))
        return result
