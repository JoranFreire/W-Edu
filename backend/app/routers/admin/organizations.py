from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_academic_staff, get_current_admin
from app.models.student import Student
from app.schemas.student import OrganizationCreate, OrganizationOut, OrganizationUpdate
from app.services.student import OrganizationService

router = APIRouter()


@router.post("/organizations", response_model=OrganizationOut, status_code=201)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin),
):
    return OrganizationService(db).create(data)


@router.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    return OrganizationService(db).list_for_user(current)


@router.patch("/organizations/{organization_id}", response_model=OrganizationOut)
def update_organization(
    organization_id: UUID,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin),
):
    return OrganizationService(db).update(organization_id, data)
