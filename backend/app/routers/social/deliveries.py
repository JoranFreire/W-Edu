from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_school_staff, get_current_student
from app.models.student import Student
from app.schemas.social_programs import DeliveryOut, IndividualDeliveryInput, MeetingDeliveryInput, MeetingDeliveryOut
from app.services.social.deliveries import BenefitDeliveryService

router = APIRouter()


@router.post("/meetings/{meeting_id}/deliveries", response_model=MeetingDeliveryOut)
def deliver_in_meeting(meeting_id: UUID, data: MeetingDeliveryInput, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return BenefitDeliveryService(db).deliver_in_meeting(meeting_id, data, current)


@router.post("/deliveries", response_model=DeliveryOut, status_code=201)
def deliver_to_student(data: IndividualDeliveryInput, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return BenefitDeliveryService(db).deliver_to_student(data, current)


@router.get("/offerings/{offering_id}/deliveries", response_model=list[DeliveryOut])
def offering_deliveries(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return BenefitDeliveryService(db).list_for_offering(offering_id, current)


@router.get("/my/benefits", response_model=list[DeliveryOut])
def my_benefits(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return BenefitDeliveryService(db).list_mine(current)
