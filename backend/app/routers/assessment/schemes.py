from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.assessment import GradingSchemeCreate, GradingSchemeOut, GradingSchemeUpdate
from app.services.assessment import GradingSchemeService

router = APIRouter(prefix="/grading-schemes")


@router.get("", response_model=list[GradingSchemeOut])
def list_schemes(db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return GradingSchemeService(db).list()


@router.post("", response_model=GradingSchemeOut, status_code=201)
def create_scheme(data: GradingSchemeCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return GradingSchemeService(db).create(data)


@router.patch("/{scheme_id}", response_model=GradingSchemeOut)
def update_scheme(
    scheme_id: int,
    data: GradingSchemeUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return GradingSchemeService(db).update(scheme_id, data)


@router.delete("/{scheme_id}", status_code=204)
def delete_scheme(scheme_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    GradingSchemeService(db).delete(scheme_id)
