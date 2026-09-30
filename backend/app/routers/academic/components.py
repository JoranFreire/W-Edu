from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator
from app.models.student import Student
from app.schemas.academic import CurriculumComponentCreate, CurriculumComponentUpdate
from app.services.academic import CurriculumComponentService

router = APIRouter()


@router.post("/curricula/{curriculum_id}/components", status_code=201)
def add_component(
    curriculum_id: int,
    data: CurriculumComponentCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
) -> dict:
    return {"id": CurriculumComponentService(db).add(curriculum_id, data).id}


@router.patch("/curriculum-components/{component_id}", status_code=204)
def update_component(
    component_id: int,
    data: CurriculumComponentUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    CurriculumComponentService(db).update(component_id, data)


@router.delete("/curriculum-components/{component_id}", status_code=204)
def remove_component(component_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    CurriculumComponentService(db).remove(component_id)
