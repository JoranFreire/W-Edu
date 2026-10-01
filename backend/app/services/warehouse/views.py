from __future__ import annotations

from datetime import date

from app.core import qr
from app.models.warehouse import MaterialRequest, RequestStatus
from app.schemas.academic_groups import PersonSummary
from app.schemas.warehouse import RequestLineOut, RequestOut
from app.services.warehouse.rules import outstanding

QR_PREFIX = "wedu-material:"


def is_overdue(request: MaterialRequest, today: date | None = None) -> bool:
    return (
        request.status == RequestStatus.delivered and request.return_due_on is not None
        and request.return_due_on < (today or date.today()) and any(outstanding(line) for line in request.lines)
    )


def request_out(request: MaterialRequest, *, with_pickup_code: bool = False) -> RequestOut:
    """`with_pickup_code`: so na visao de quem pediu, e so enquanto a requisicao espera a retirada."""
    code = request.pickup_code if with_pickup_code and request.status == RequestStatus.approved else None
    return RequestOut(
        id=request.id, requester=PersonSummary.model_validate(request.requester), class_offering_id=request.class_offering_id,
        class_offering_name=request.class_offering.name if request.class_offering else None, purpose=request.purpose,
        needed_on=request.needed_on, status=request.status, decision_note=request.decision_note, decided_at=request.decided_at,
        delivered_at=request.delivered_at, delivered_by_name=request.delivered_by.name if request.delivered_by else None,
        delivery_method=request.delivery_method, delivery_note=request.delivery_note,
        pickup_code=code, qr_payload=qr.qr_payload(QR_PREFIX, code) if code else None, return_due_on=request.return_due_on, overdue=is_overdue(request), created_at=request.created_at,
        lines=[
            RequestLineOut(
                id=line.id, item_id=line.item_id, item_name=line.item.name, kind=line.item.kind, unit=line.item.unit,
                quantity_requested=line.quantity_requested, quantity_approved=line.quantity_approved,
                quantity_delivered=line.quantity_delivered, quantity_returned=line.quantity_returned,
                quantity_lost=line.quantity_lost, outstanding=outstanding(line),
            )
            for line in request.lines
        ],
    )
