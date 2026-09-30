from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_guardian
from app.models.student import Student
from app.schemas.school_life import AgendaItemOut, OccurrenceOut
from app.services.guardians.school_life import GuardianSchoolLifeService

router = APIRouter(prefix="/me/dependents")


@router.get("/{student_id}/occurrences", response_model=list[OccurrenceOut])
def dependent_occurrences(student_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianSchoolLifeService(db).occurrences_of(current, student_id)


@router.post("/{student_id}/occurrences/{occurrence_id}/acknowledge", response_model=OccurrenceOut)
def acknowledge_occurrence(
    student_id: int, occurrence_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian),
):
    return GuardianSchoolLifeService(db).acknowledge(current, student_id, occurrence_id)


@router.get("/{student_id}/agenda", response_model=list[AgendaItemOut])
def dependent_agenda(
    student_id: int, from_date: date | None = None, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian),
):
    return GuardianSchoolLifeService(db).agenda_of(current, student_id, from_date)
