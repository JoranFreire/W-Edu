from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic import CurriculumCreate, CurriculumDetail, CurriculumNewVersion, CurriculumOut, CurriculumUpdate
from app.services.academic import CurriculumService

router = APIRouter()


@router.get("/programs/{program_id}/curricula", response_model=list[CurriculumOut])
def list_curricula(program_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return CurriculumService(db).list_by_program(program_id)


@router.post("/programs/{program_id}/curricula", response_model=CurriculumOut, status_code=201)
def create_curriculum(
    program_id: UUID,
    data: CurriculumCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return CurriculumService(db).create(program_id, data)


@router.get("/curricula/{curriculum_id}", response_model=CurriculumDetail)
def get_curriculum(curriculum_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return CurriculumService(db).detail(curriculum_id)


@router.patch("/curricula/{curriculum_id}", response_model=CurriculumOut)
def update_curriculum(
    curriculum_id: UUID,
    data: CurriculumUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return CurriculumService(db).update(curriculum_id, data)


@router.delete("/curricula/{curriculum_id}", status_code=204)
def delete_curriculum(curriculum_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    CurriculumService(db).delete(curriculum_id)


@router.post("/curricula/{curriculum_id}/activate", response_model=CurriculumOut)
def activate_curriculum(curriculum_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return CurriculumService(db).activate(curriculum_id)


@router.post("/curricula/{curriculum_id}/archive", response_model=CurriculumOut)
def archive_curriculum(curriculum_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return CurriculumService(db).archive(curriculum_id)


@router.post("/curricula/{curriculum_id}/versions", response_model=CurriculumOut, status_code=201)
def new_curriculum_version(
    curriculum_id: UUID,
    data: CurriculumNewVersion,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return CurriculumService(db).new_version(curriculum_id, data)
