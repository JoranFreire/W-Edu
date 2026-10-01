from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_student, get_current_teaching_staff
from app.models.student import Student
from app.schemas.completion import InternshipCreate, InternshipLogCreate, InternshipLogOut, InternshipOut, InternshipUpdate, LogReview
from app.services.completion.internship_logs import InternshipLogService
from app.services.completion.internships import InternshipService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/internships", response_model=list[InternshipOut])
def enrollment_internships(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return InternshipService(db).list_for_enrollment(enrollment_id)


@router.post("/enrollments/{enrollment_id}/internships", response_model=InternshipOut, status_code=201)
def create_internship(enrollment_id: UUID, data: InternshipCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return InternshipService(db).create(enrollment_id, data)


@router.patch("/internships/{internship_id}", response_model=InternshipOut)
def update_internship(internship_id: UUID, data: InternshipUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return InternshipService(db).update(internship_id, data)


@router.get("/my/internships", response_model=list[InternshipOut])
def my_internships(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return InternshipService(db).list_mine(current)


@router.get("/internships/{internship_id}/logs", response_model=list[InternshipLogOut])
def internship_logs(internship_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return InternshipLogService(db).list(internship_id, current)


@router.post("/my/internships/{internship_id}/logs", response_model=InternshipLogOut, status_code=201)
def add_internship_log(internship_id: UUID, data: InternshipLogCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return InternshipLogService(db).add(current, internship_id, data)


@router.delete("/my/internship-logs/{log_id}", status_code=204)
def remove_internship_log(log_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    InternshipLogService(db).remove(current, log_id)


@router.post("/internship-logs/{log_id}/review", response_model=InternshipLogOut)
def review_internship_log(log_id: UUID, data: LogReview, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return InternshipLogService(db).review(log_id, data.approved, current)
