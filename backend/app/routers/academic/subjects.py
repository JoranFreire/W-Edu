from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic import SubjectCreate, SubjectOut, SubjectUpdate
from app.services.academic import SubjectService

router = APIRouter(prefix="/subjects")


@router.get("", response_model=list[SubjectOut])
def list_subjects(
    search: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_student),
):
    return SubjectService(db).list(search=search, active=active)


@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return SubjectService(db).create(data)


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return SubjectService(db).get_or_404(subject_id)


@router.patch("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return SubjectService(db).update(subject_id, data)


@router.delete("/{subject_id}", status_code=204)
def delete_subject(subject_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    SubjectService(db).delete(subject_id)
