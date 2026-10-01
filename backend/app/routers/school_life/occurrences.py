from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_school_staff
from app.models.student import Student
from app.schemas.school_life import OccurrenceCreate, OccurrenceOut
from app.services.school_life.occurrences import OccurrenceService

router = APIRouter()


@router.get("/students/{student_id}/occurrences", response_model=list[OccurrenceOut])
def list_occurrences(student_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return OccurrenceService(db).list_for_student(student_id, current)


@router.post("/occurrences", response_model=OccurrenceOut, status_code=201)
def register_occurrence(data: OccurrenceCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return OccurrenceService(db).register(data, current)


@router.delete("/occurrences/{occurrence_id}", status_code=204)
def remove_occurrence(occurrence_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    OccurrenceService(db).remove(occurrence_id, current)
