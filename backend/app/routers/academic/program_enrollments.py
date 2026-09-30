from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_secretariat, get_current_student
from app.models.academic_groups import ProgramEnrollmentStatus
from app.models.student import Student
from app.schemas.academic_groups import ProgramEnrollmentCreate, ProgramEnrollmentOut, ProgramEnrollmentStatusChange
from app.services.academic import ProgramEnrollmentService

router = APIRouter(prefix="/program-enrollments")


@router.get("", response_model=list[ProgramEnrollmentOut])
def list_program_enrollments(
    program_id: int | None = None,
    status: ProgramEnrollmentStatus | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_secretariat),
):
    return ProgramEnrollmentService(db).list(program_id=program_id, status=status, student_id=student_id)


@router.get("/me", response_model=list[ProgramEnrollmentOut])
def my_program_enrollments(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ProgramEnrollmentService(db).list(student_id=current.id)


@router.post("", response_model=ProgramEnrollmentOut, status_code=201)
def create_program_enrollment(
    data: ProgramEnrollmentCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_secretariat),
):
    return ProgramEnrollmentService(db).create(data, user_id=current.id)


@router.post("/{enrollment_id}/status", response_model=ProgramEnrollmentOut)
def change_program_enrollment_status(
    enrollment_id: int,
    data: ProgramEnrollmentStatusChange,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_admin_or_coordinator),
):
    return ProgramEnrollmentService(db).change_status(enrollment_id, data.status, user_id=current.id)
