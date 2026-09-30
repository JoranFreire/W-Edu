from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator
from app.models.student import Student
from app.schemas.enrollment import EnrollmentOut
from app.services.enrollment import EnrollmentService

router = APIRouter()


@router.get("/enrollments/course/{course_id}", response_model=list[EnrollmentOut])
def enrollments_by_course(course_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return EnrollmentService(db).list_by_course(course_id)
