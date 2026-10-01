from __future__ import annotations

from datetime import date

from app.models.warehouse import MaterialRequest, RequestStatus
from app.schemas.academic_groups import PersonSummary
from app.schemas.warehouse import RequestLineOut, RequestOut
from app.services.warehouse.rules import outstanding


def is_overdue(request: MaterialRequest, today: date | None = None) -> bool:
    return (
        request.status == RequestStatus.delivered and request.return_due_on is not None
        and request.return_due_on < (today or date.today()) and any(outstanding(line) for line in request.lines)
    )


def request_out(request: MaterialRequest) -> RequestOut:
    return RequestOut(
        id=request.id, requester=PersonSummary.model_validate(request.requester), class_offering_id=request.class_offering_id,
        class_offering_name=request.class_offering.name if request.class_offering else None, purpose=request.purpose,
        needed_on=request.needed_on, status=request.status, decision_note=request.decision_note, decided_at=request.decided_at,
        delivered_at=request.delivered_at, return_due_on=request.return_due_on, overdue=is_overdue(request), created_at=request.created_at,
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
