from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.course_registration import TimeSlotCreate, TimeSlotOut
from app.services.registration.time_slots import OfferingTimeSlotService

router = APIRouter()


@router.get("/offerings/{offering_id}/time-slots", response_model=list[TimeSlotOut])
def list_time_slots(offering_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return OfferingTimeSlotService(db).list(offering_id)


@router.post("/offerings/{offering_id}/time-slots", response_model=TimeSlotOut, status_code=201)
def add_time_slot(offering_id: int, data: TimeSlotCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return OfferingTimeSlotService(db).add(offering_id, data)


@router.delete("/time-slots/{slot_id}", status_code=204)
def remove_time_slot(slot_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    OfferingTimeSlotService(db).remove(slot_id)
