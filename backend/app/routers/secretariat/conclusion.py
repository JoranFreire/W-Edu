from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.academic_groups import ProgramEnrollmentOut
from app.schemas.secretariat import CeremonyInput, ConclusionCheckOut, ConclusionInput
from app.services.secretariat.conclusion import ConclusionService

router = APIRouter(prefix="/enrollments/{enrollment_id}")


@router.get("/conclusion", response_model=ConclusionCheckOut)
def check_conclusion(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ConclusionService(db).check(enrollment_id)


@router.post("/conclusion", response_model=ProgramEnrollmentOut)
def conclude_program(
    enrollment_id: UUID,
    data: ConclusionInput,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_secretariat),
):
    return ConclusionService(db).conclude(enrollment_id, data.concluded_on, data.ceremony_on, current.id)


@router.put("/ceremony", response_model=ProgramEnrollmentOut)
def set_ceremony(enrollment_id: UUID, data: CeremonyInput, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ConclusionService(db).set_ceremony(enrollment_id, data.ceremony_on)
