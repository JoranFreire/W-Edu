from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.academic_groups import PersonSummary
from app.services.secretariat.students import StudentDirectoryService

router = APIRouter()


@router.get("/students", response_model=list[PersonSummary])
def list_students(db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return StudentDirectoryService(db).list()
