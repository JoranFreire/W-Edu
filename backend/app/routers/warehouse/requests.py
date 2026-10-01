from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_warehouse_requester
from app.models.student import Student
from app.schemas.warehouse import RequestCreate, RequestOut
from app.services.warehouse.requests import MaterialRequestService

router = APIRouter()


@router.post("/requests", response_model=RequestOut, status_code=201)
def create_request(data: RequestCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_requester)):
    return MaterialRequestService(db).create(current, data)


@router.get("/my/requests", response_model=list[RequestOut])
def my_requests(db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_requester)):
    return MaterialRequestService(db).list_mine(current)


@router.post("/my/requests/{request_id}/cancel", response_model=RequestOut)
def cancel_request(request_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_requester)):
    return MaterialRequestService(db).cancel(current, request_id)
