from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.course_registration import RegistrationWindowCreate, RegistrationWindowOut, RegistrationWindowUpdate
from app.services.registration.windows import RegistrationWindowService

router = APIRouter(prefix="/windows")


@router.get("", response_model=list[RegistrationWindowOut])
def list_windows(term_id: UUID | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RegistrationWindowService(db).list(term_id)


@router.post("", response_model=RegistrationWindowOut, status_code=201)
def create_window(data: RegistrationWindowCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RegistrationWindowService(db).create(data)


@router.patch("/{window_id}", response_model=RegistrationWindowOut)
def update_window(window_id: UUID, data: RegistrationWindowUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RegistrationWindowService(db).update(window_id, data)


@router.delete("/{window_id}", status_code=204)
def delete_window(window_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    RegistrationWindowService(db).delete(window_id)
