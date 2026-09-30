from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import AssessmentItemCreate, AssessmentItemOut, AssessmentItemUpdate
from app.services.assessment import AssessmentItemService

router = APIRouter()


@router.get("/offerings/{offering_id}/items", response_model=list[AssessmentItemOut])
def list_items(offering_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return AssessmentItemService(db).list(offering_id, current)


@router.post("/offerings/{offering_id}/items", response_model=AssessmentItemOut, status_code=201)
def create_item(
    offering_id: int,
    data: AssessmentItemCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_teaching_staff),
):
    return AssessmentItemService(db).create(offering_id, data, current)


@router.patch("/items/{item_id}", response_model=AssessmentItemOut)
def update_item(item_id: int, data: AssessmentItemUpdate, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return AssessmentItemService(db).update(item_id, data, current)


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    AssessmentItemService(db).delete(item_id, current)
