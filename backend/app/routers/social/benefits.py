from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_school_staff, get_current_secretariat
from app.models.student import Student
from app.schemas.social_programs import BenefitItemCreate, BenefitItemOut, BenefitItemUpdate, StockEntryCreate, StockEntryOut
from app.services.social.benefits import BenefitCatalogService

router = APIRouter(prefix="/benefit-items")


@router.get("", response_model=list[BenefitItemOut])
def list_items(db: Session = Depends(get_db), _: Student = Depends(get_current_school_staff)):
    return BenefitCatalogService(db).list()


@router.post("", response_model=BenefitItemOut, status_code=201)
def create_item(data: BenefitItemCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return BenefitCatalogService(db).create(data)


@router.patch("/{item_id}", response_model=BenefitItemOut)
def update_item(item_id: UUID, data: BenefitItemUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return BenefitCatalogService(db).update(item_id, data)


@router.get("/{item_id}/stock", response_model=list[StockEntryOut])
def stock_entries(item_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return BenefitCatalogService(db).entries(item_id)


@router.post("/{item_id}/stock", response_model=BenefitItemOut, status_code=201)
def receive_stock(item_id: UUID, data: StockEntryCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return BenefitCatalogService(db).receive(item_id, data, current)
