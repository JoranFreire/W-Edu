from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_institution, get_current_student
from app.models.institution import Institution
from app.models.student import Student
from app.schemas.institution import CampusCreate, CampusOut, CampusUpdate, InstitutionOut, InstitutionUpdate
from app.services.campus import CampusService
from app.services.institution import InstitutionService

router = APIRouter()


@router.get("/current", response_model=InstitutionOut)
def get_current(institution: Institution = Depends(get_current_institution)):
    return institution


@router.patch("/current", response_model=InstitutionOut)
def update_current(
    data: InstitutionUpdate,
    db: Session = Depends(get_db),
    institution: Institution = Depends(get_current_institution),
    _: Student = Depends(get_current_admin),
):
    return InstitutionService(db).update(institution, data)


@router.get("/campuses", response_model=list[CampusOut])
def list_campuses(db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return CampusService(db).list()


@router.post("/campuses", response_model=CampusOut, status_code=201)
def create_campus(data: CampusCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return CampusService(db).create(data)


@router.patch("/campuses/{campus_id}", response_model=CampusOut)
def update_campus(campus_id: int, data: CampusUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return CampusService(db).update(campus_id, data)


@router.delete("/campuses/{campus_id}", status_code=204)
def delete_campus(campus_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    CampusService(db).delete(campus_id)
