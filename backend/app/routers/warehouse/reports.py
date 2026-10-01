from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_warehouse_reader
from app.models.student import Student
from app.schemas.warehouse import ConsumptionOut, ItemOut, RequestOut
from app.services.warehouse.reports import WarehouseReportService

router = APIRouter(prefix="/reports")


@router.get("/low-stock", response_model=list[ItemOut])
def low_stock(db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_reader)):
    return WarehouseReportService(db).low_stock()


@router.get("/overdue", response_model=list[RequestOut])
def overdue(db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_reader)):
    return WarehouseReportService(db).overdue()


@router.get("/consumption", response_model=ConsumptionOut)
def consumption(start: date, end: date, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_reader)):
    return WarehouseReportService(db).consumption(start, end)
