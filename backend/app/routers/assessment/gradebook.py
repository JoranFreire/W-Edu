from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import GradebookOut
from app.services.assessment import GradebookService

router = APIRouter()


@router.get("/offerings/{offering_id}/gradebook", response_model=GradebookOut)
def get_gradebook(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return GradebookService(db).build(offering_id, current)
