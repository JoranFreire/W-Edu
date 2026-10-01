from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_public_institution
from app.models.institution import Institution
from app.schemas.admissions import AdmissionCallOut, AdmissionResultOut
from app.services.admissions.public import PublicAdmissionsService

router = APIRouter(prefix="/public/calls")


@router.get("", response_model=list[AdmissionCallOut])
def public_calls(db: Session = Depends(get_db), _: Institution = Depends(get_public_institution)):
    return PublicAdmissionsService(db).catalog()


@router.get("/{call_id}", response_model=AdmissionCallOut)
def public_call(call_id: UUID, db: Session = Depends(get_db), _: Institution = Depends(get_public_institution)):
    return PublicAdmissionsService(db).detail(call_id)


@router.get("/{call_id}/result", response_model=AdmissionResultOut)
def public_result(call_id: UUID, db: Session = Depends(get_db), _: Institution = Depends(get_public_institution)):
    return PublicAdmissionsService(db).result(call_id)
