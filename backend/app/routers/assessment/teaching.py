from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import SyncEnrollmentsResult, TeachingOfferingOut
from app.services.assessment import TeachingOfferingService

router = APIRouter()


@router.get("/teaching/offerings", response_model=list[TeachingOfferingOut])
def list_teaching_offerings(db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return TeachingOfferingService(db).list_for(current)


@router.get("/offerings/{offering_id}", response_model=TeachingOfferingOut)
def get_teaching_offering(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return TeachingOfferingService(db).get_for_teaching(offering_id, current)


@router.post("/offerings/{offering_id}/sync-group-enrollments", response_model=SyncEnrollmentsResult)
def sync_group_enrollments(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_admin_or_coordinator)):
    return TeachingOfferingService(db).sync_group_enrollments(offering_id, current)
