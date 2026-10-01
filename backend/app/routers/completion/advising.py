from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_teaching_staff
from app.models.student import Student
from app.schemas.academic_groups import PersonSummary
from app.schemas.completion import AdvisingOut
from app.services.completion.advising import AdvisingService
from app.services.completion.advisors import AdvisorDirectory

router = APIRouter()


@router.get("/advising", response_model=AdvisingOut)
def my_advising(db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return AdvisingService(db).for_user(current)


@router.get("/advisors", response_model=list[PersonSummary])
def list_advisors(db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdvisorDirectory(db).list()
