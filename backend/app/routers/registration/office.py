from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.course_registration import OfficeRegistrationInput, RegistrationCatalogOut, RegistrationResultOut
from app.services.registration.catalog import RegistrationCatalogService
from app.services.registration.enrollment import SubjectRegistrationService

router = APIRouter(prefix="/program-enrollments/{program_enrollment_id}")


@router.get("/terms/{term_id}/catalog", response_model=RegistrationCatalogOut)
def enrollment_catalog(program_enrollment_id: UUID, term_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RegistrationCatalogService(db).for_enrollment(program_enrollment_id, term_id)


@router.post("/offerings/{offering_id}", response_model=RegistrationResultOut)
def register_by_office(
    program_enrollment_id: UUID, offering_id: UUID, data: OfficeRegistrationInput,
    db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat),
):
    return SubjectRegistrationService(db).register_by_office(program_enrollment_id, offering_id, data.override)


@router.delete("/offerings/{offering_id}", status_code=204)
def drop_by_office(program_enrollment_id: UUID, offering_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    SubjectRegistrationService(db).drop_by_office(program_enrollment_id, offering_id)
