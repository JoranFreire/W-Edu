from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_student, get_current_teaching_staff
from app.models.student import Student
from app.schemas.completion import FinalProjectInput, FinalProjectOut, FinalProjectResult
from app.services.completion.final_projects import FinalProjectService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/final-project", response_model=FinalProjectOut | None)
def enrollment_final_project(enrollment_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return FinalProjectService(db).get_for_enrollment(enrollment_id)


@router.put("/enrollments/{enrollment_id}/final-project", response_model=FinalProjectOut)
def save_final_project(enrollment_id: int, data: FinalProjectInput, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return FinalProjectService(db).save(enrollment_id, data)


@router.post("/final-projects/{project_id}/result", response_model=FinalProjectOut)
def record_final_project(project_id: int, data: FinalProjectResult, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return FinalProjectService(db).record(project_id, data, current)


@router.get("/my/final-projects", response_model=list[FinalProjectOut])
def my_final_projects(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return FinalProjectService(db).list_mine(current)
