from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.models.warehouse import MaterialRequest, RequestStatus
from app.repositories.warehouse import MaterialRequestRepository
from app.schemas.warehouse import ConsumptionOut, ConsumptionRow, ItemOut, RequestOut
from app.services.warehouse.catalog import WarehouseCatalogService
from app.services.warehouse.views import is_overdue, request_out


def consumption(requests: list[MaterialRequest]) -> ConsumptionOut:
    """Consumo = o que saiu e nao voltou (consumido, perdido ou ainda emprestado), com custo da retirada."""
    groups = {"item": defaultdict(lambda: [0, 0]), "requester": defaultdict(lambda: [0, 0]), "offering": defaultdict(lambda: [0, 0])}
    for request in requests:
        for line in request.lines:
            used = line.quantity_delivered - line.quantity_returned
            if used <= 0:
                continue
            cost = used * line.unit_cost_cents
            for key, label in (("item", line.item.name), ("requester", request.requester.name),
                               ("offering", request.class_offering.name if request.class_offering else "Sem turma")):
                groups[key][label][0] += used
                groups[key][label][1] += cost

    def rows(key: str) -> list[ConsumptionRow]:
        return sorted((ConsumptionRow(label=label, quantity=q, cost_cents=c) for label, (q, c) in groups[key].items()), key=lambda r: -r.cost_cents)

    return ConsumptionOut(
        by_item=rows("item"), by_requester=rows("requester"), by_offering=rows("offering"),
        total_cost_cents=sum(c for _, c in groups["item"].values()),
    )


class WarehouseReportService:
    """Estoque abaixo do minimo, emprestimos em atraso e consumo no periodo."""

    def __init__(self, db: Session):
        self.repo = MaterialRequestRepository(db)
        self.catalog = WarehouseCatalogService(db)

    def low_stock(self) -> list[ItemOut]:
        return [item for item in self.catalog.list(only_active=True) if item.below_minimum]

    def overdue(self) -> list[RequestOut]:
        today = date.today()
        return [request_out(r) for r in self.repo.list(status=RequestStatus.delivered) if is_overdue(r, today)]

    def consumption(self, start: date, end: date) -> ConsumptionOut:
        return consumption(self.repo.delivered_between(start, end))
