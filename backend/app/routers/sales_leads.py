from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_super_admin
from app.models.sales import LeadStatus
from app.models.student import Student
from app.schemas.public_site import SalesLeadOut, SalesLeadUpdate
from app.services.sales.leads import SalesLeadService

router = APIRouter()


@router.get("", response_model=list[SalesLeadOut])
def list_leads(status: LeadStatus | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return SalesLeadService(db).list(status)


@router.patch("/{lead_id}", response_model=SalesLeadOut)
def update_lead(lead_id: UUID, data: SalesLeadUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return SalesLeadService(db).update(lead_id, data)
