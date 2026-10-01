from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_super_admin
from app.models.student import Student
from app.schemas.institution import CampusOut, InstitutionCreate, InstitutionOut, PlatformInstitutionUpdate
from app.services.campus import CampusService
from app.services.institution import InstitutionService

router = APIRouter()


@router.get("/institutions", response_model=list[InstitutionOut])
def list_institutions(db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return InstitutionService(db).list_all()


@router.post("/institutions", response_model=InstitutionOut, status_code=201)
def create_institution(data: InstitutionCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return InstitutionService(db).create(data)


@router.get("/institutions/{institution_id}", response_model=InstitutionOut)
def get_institution(institution_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return InstitutionService(db).get_or_404(institution_id)


@router.patch("/institutions/{institution_id}", response_model=InstitutionOut)
def update_institution(
    institution_id: UUID,
    data: PlatformInstitutionUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_super_admin),
):
    service = InstitutionService(db)
    return service.update(service.get_or_404(institution_id), data)


@router.get("/institutions/{institution_id}/campuses", response_model=list[CampusOut])
def list_institution_campuses(institution_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    institution = InstitutionService(db).get_or_404(institution_id)
    return CampusService(db).list(institution.id)
