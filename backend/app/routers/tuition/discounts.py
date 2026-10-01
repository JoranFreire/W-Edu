from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_finance_staff
from app.models.student import Student
from app.schemas.tuition import DiscountCreate, DiscountOut
from app.services.tuition.discounts import StudentDiscountService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/discounts", response_model=list[DiscountOut])
def list_discounts(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_finance_staff)):
    return StudentDiscountService(db).list(enrollment_id)


@router.post("/enrollments/{enrollment_id}/discounts", response_model=DiscountOut, status_code=201)
def create_discount(enrollment_id: UUID, data: DiscountCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_finance_staff)):
    return StudentDiscountService(db).create(enrollment_id, data)


@router.post("/discounts/{discount_id}/deactivate", response_model=DiscountOut)
def deactivate_discount(discount_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_finance_staff)):
    return StudentDiscountService(db).deactivate(discount_id)
