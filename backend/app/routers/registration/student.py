from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.schemas.course_registration import MyRegistrationWindowOut, RegistrationCatalogOut, RegistrationResultOut
from app.services.registration.access import StudentWindowAccess
from app.services.registration.catalog import RegistrationCatalogService
from app.services.registration.enrollment import SubjectRegistrationService

router = APIRouter(prefix="/my/windows")


@router.get("", response_model=list[MyRegistrationWindowOut])
def my_open_windows(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return StudentWindowAccess(db).open_windows(current)


@router.get("/{window_id}/catalog", response_model=RegistrationCatalogOut)
def my_catalog(window_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return RegistrationCatalogService(db).for_window(current, window_id)


@router.post("/{window_id}/offerings/{offering_id}", response_model=RegistrationResultOut)
def register_offering(window_id: int, offering_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return SubjectRegistrationService(db).register_in_window(current, window_id, offering_id)


@router.delete("/{window_id}/offerings/{offering_id}", status_code=204)
def drop_offering(window_id: int, offering_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    SubjectRegistrationService(db).drop_in_window(current, window_id, offering_id)
