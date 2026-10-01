from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_student
from app.models.student import Student
from app.schemas.completion import IntegralizationOut
from app.services.completion.integralization import IntegralizationService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/integralization", response_model=IntegralizationOut)
def enrollment_integralization(enrollment_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return IntegralizationService(db).for_enrollment(enrollment_id)


@router.get("/my/integralization", response_model=list[IntegralizationOut])
def my_integralization(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return IntegralizationService(db).for_student(current)
