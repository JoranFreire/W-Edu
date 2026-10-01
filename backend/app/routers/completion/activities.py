from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_student
from app.models.student import Student
from app.schemas.completion import ActivityCreate, ActivityDecision, ActivityOut
from app.services.completion.activities import ComplementaryActivityService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/activities", response_model=list[ActivityOut])
def enrollment_activities(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ComplementaryActivityService(db).list_for_enrollment(enrollment_id)


@router.post("/activities/{activity_id}/decision", response_model=ActivityOut)
def decide_activity(activity_id: UUID, data: ActivityDecision, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return ComplementaryActivityService(db).decide(activity_id, data, current)


@router.get("/my/activities", response_model=list[ActivityOut])
def my_activities(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ComplementaryActivityService(db).list_mine(current)


@router.post("/my/enrollments/{enrollment_id}/activities", response_model=ActivityOut, status_code=201)
def submit_activity(enrollment_id: UUID, data: ActivityCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ComplementaryActivityService(db).submit(current, enrollment_id, data)


@router.delete("/my/activities/{activity_id}", status_code=204)
def withdraw_activity(activity_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    ComplementaryActivityService(db).withdraw(current, activity_id)
