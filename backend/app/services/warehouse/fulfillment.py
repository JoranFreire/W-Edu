from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.warehouse import MaterialRequest, RequestStatus
from app.repositories.warehouse import MaterialRequestRepository, WarehouseItemRepository
from app.schemas.warehouse import RequestOut, ReturnInput
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.warehouse.catalog import WarehouseCatalogService
from app.services.warehouse.rules import outstanding, validate_return
from app.services.warehouse.views import request_out


class MaterialFulfillmentService:
    """Retirada do que foi aprovado (com saldo) e devolucao dos permanentes, com avaria ou perda."""

    def __init__(self, db: Session):
        self.repo = MaterialRequestRepository(db)
        self.items = WarehouseItemRepository(db)
        self.catalog = WarehouseCatalogService(db)

    def deliver(self, request_id: int, operator: Student) -> RequestOut:
        request = self._get(request_id)
        if request.status != RequestStatus.approved:
            raise conflict("Só requisições aprovadas são retiradas")
        lines = [line for line in request.lines if line.quantity_approved]
        locked = self.items.lock_many([line.item_id for line in lines])
        balances = self.catalog.balances(list(locked))
        short = [f"{line.item.name} ({balances[line.item_id]} disponível(is))" for line in lines if line.quantity_approved > balances[line.item_id]]
        if short:
            raise conflict("Saldo insuficiente: " + ", ".join(short))
        for line in lines:
            line.quantity_delivered, line.unit_cost_cents = line.quantity_approved, locked[line.item_id].unit_cost_cents
        request.delivered_by_id, request.delivered_at = operator.id, datetime.now(timezone.utc)
        request.status = RequestStatus.delivered if any(outstanding(line) for line in lines) else RequestStatus.closed
        self.repo.commit()
        return request_out(request)

    def register_return(self, request_id: int, data: ReturnInput) -> RequestOut:
        request = self._get(request_id)
        if request.status != RequestStatus.delivered:
            raise conflict("Não há materiais emprestados nesta requisição")
        by_id = {line.id: line for line in request.lines}
        for item in data.lines:
            line = by_id.get(item.line_id)
            if line is None:
                raise bad_request("Linha não pertence à requisição")
            if problem := validate_return(line, item.returned, item.lost):
                raise bad_request(problem)
            line.quantity_returned += item.returned
            line.quantity_lost += item.lost
        if not any(outstanding(line) for line in request.lines):
            request.status = RequestStatus.closed
        self.repo.commit()
        return request_out(request)

    def _get(self, request_id: int) -> MaterialRequest:
        request = self.repo.get(request_id)
        if not request:
            raise not_found("Requisição não encontrada")
        return request
