from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic_calendar import CalendarEventCreate, CalendarEventOut, CalendarEventUpdate
from app.services.academic import CalendarEventService

router = APIRouter(prefix="/calendar-events")


@router.get("", response_model=list[CalendarEventOut])
def list_calendar_events(
    term_id: UUID | None = None,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_student),
):
    return CalendarEventService(db).list(term_id=term_id, start=start, end=end)


@router.post("", response_model=CalendarEventOut, status_code=201)
def create_calendar_event(
    data: CalendarEventCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return CalendarEventService(db).create(data)


@router.patch("/{event_id}", response_model=CalendarEventOut)
def update_calendar_event(
    event_id: UUID,
    data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return CalendarEventService(db).update(event_id, data)


@router.delete("/{event_id}", status_code=204)
def delete_calendar_event(event_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    CalendarEventService(db).delete(event_id)
