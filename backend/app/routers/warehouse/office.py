from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_warehouse_manager
from app.models.student import Student
from app.models.warehouse import RequestStatus
from app.schemas.warehouse import ApprovalInput, ManualDeliveryInput, PickupCodeInput, RejectInput, RequestOut, ReturnInput
from app.services.warehouse.fulfillment import MaterialFulfillmentService
from app.services.warehouse.review import MaterialRequestReviewService

router = APIRouter(prefix="/requests")


@router.get("", response_model=list[RequestOut])
def list_requests(status: RequestStatus | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).list(status)


# Antes das rotas com {request_id}: "lookup" e "pickup" nao sao ids.
@router.post("/lookup", response_model=RequestOut)
def lookup_by_qr(data: PickupCodeInput, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    # POST: o codigo do QR nao vai para a URL (logs de acesso).
    return MaterialFulfillmentService(db).lookup(data.code)


@router.post("/pickup", response_model=RequestOut)
def pickup_by_qr(data: PickupCodeInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialFulfillmentService(db).pickup(data.code, current)


@router.post("/{request_id}/approve", response_model=RequestOut)
def approve(request_id: UUID, data: ApprovalInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).approve(request_id, data, current)


@router.post("/{request_id}/reject", response_model=RequestOut)
def reject(request_id: UUID, data: RejectInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).reject(request_id, data, current)


@router.post("/{request_id}/deliver", response_model=RequestOut)
def deliver(request_id: UUID, data: ManualDeliveryInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    """Retirada sem o QR: exige o motivo, que fica no historico."""
    return MaterialFulfillmentService(db).deliver(request_id, current, data.note)


@router.post("/{request_id}/returns", response_model=RequestOut)
def register_return(request_id: UUID, data: ReturnInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialFulfillmentService(db).register_return(request_id, data, current)
