from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import GradeInput, GradeRow, QuizImportResult
from app.services.assessment import GradeService

router = APIRouter(prefix="/items/{item_id}")


@router.get("/grades", response_model=list[GradeRow])
def list_grades(item_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return GradeService(db).list(item_id, current)


@router.put("/grades", response_model=list[GradeRow])
def save_grades(item_id: int, data: list[GradeInput], db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return GradeService(db).save(item_id, data, current)


@router.post("/import-quiz", response_model=QuizImportResult)
def import_quiz_scores(item_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return GradeService(db).import_quiz(item_id, current)
