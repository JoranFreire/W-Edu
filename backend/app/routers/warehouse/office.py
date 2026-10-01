from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_warehouse_manager
from app.models.student import Student
from app.models.warehouse import RequestStatus
from app.schemas.warehouse import ApprovalInput, RejectInput, RequestOut, ReturnInput
from app.services.warehouse.fulfillment import MaterialFulfillmentService
from app.services.warehouse.review import MaterialRequestReviewService

router = APIRouter(prefix="/requests")


@router.get("", response_model=list[RequestOut])
def list_requests(status: RequestStatus | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).list(status)


@router.post("/{request_id}/approve", response_model=RequestOut)
def approve(request_id: UUID, data: ApprovalInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).approve(request_id, data, current)


@router.post("/{request_id}/reject", response_model=RequestOut)
def reject(request_id: UUID, data: RejectInput, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialRequestReviewService(db).reject(request_id, data, current)


@router.post("/{request_id}/deliver", response_model=RequestOut)
def deliver(request_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return MaterialFulfillmentService(db).deliver(request_id, current)


@router.post("/{request_id}/returns", response_model=RequestOut)
def register_return(request_id: UUID, data: ReturnInput, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return MaterialFulfillmentService(db).register_return(request_id, data)
