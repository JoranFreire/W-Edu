from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic_calendar import (
    AcademicTermCreate,
    AcademicTermOut,
    AcademicTermUpdate,
    TermCalendarSummary,
    TermStatusChange,
)
from app.services.academic import AcademicTermService, CalendarEventService

router = APIRouter(prefix="/terms")


@router.get("", response_model=list[AcademicTermOut])
def list_terms(db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return AcademicTermService(db).list()


@router.post("", response_model=AcademicTermOut, status_code=201)
def create_term(data: AcademicTermCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return AcademicTermService(db).create(data)


@router.get("/{term_id}", response_model=AcademicTermOut)
def get_term(term_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return AcademicTermService(db).get_or_404(term_id)


@router.patch("/{term_id}", response_model=AcademicTermOut)
def update_term(
    term_id: int,
    data: AcademicTermUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return AcademicTermService(db).update(term_id, data)


@router.post("/{term_id}/status", response_model=AcademicTermOut)
def change_term_status(
    term_id: int,
    data: TermStatusChange,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return AcademicTermService(db).change_status(term_id, data.status)


@router.delete("/{term_id}", status_code=204)
def delete_term(term_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    AcademicTermService(db).delete(term_id)


@router.get("/{term_id}/calendar-summary", response_model=TermCalendarSummary)
def term_calendar_summary(term_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return CalendarEventService(db).summary(term_id)
