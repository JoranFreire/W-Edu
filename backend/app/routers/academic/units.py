from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic import AcademicUnitCreate, AcademicUnitOut, AcademicUnitUpdate
from app.services.academic import AcademicUnitService

router = APIRouter(prefix="/units")


@router.get("", response_model=list[AcademicUnitOut])
def list_units(db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return AcademicUnitService(db).list()


@router.post("", response_model=AcademicUnitOut, status_code=201)
def create_unit(data: AcademicUnitCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return AcademicUnitService(db).create(data)


@router.patch("/{unit_id}", response_model=AcademicUnitOut)
def update_unit(
    unit_id: int,
    data: AcademicUnitUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return AcademicUnitService(db).update(unit_id, data)


@router.delete("/{unit_id}", status_code=204)
def delete_unit(unit_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    AcademicUnitService(db).delete(unit_id)
