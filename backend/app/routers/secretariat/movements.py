"""Movimentacoes da matricula: rematricula, trancamento, reativacao, cancelamento e transferencias."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.academic_groups import ProgramEnrollmentStatus
from app.models.student import Student
from app.schemas.academic_groups import ProgramEnrollmentOut
from app.schemas.secretariat import (
    CurriculumChangeInput,
    EnrollmentEventOut,
    InternalTransferInput,
    ReasonInput,
    ReenrollInput,
    TermRegistrationOut,
    TransferOutInput,
)
from app.services.academic.program_enrollments import ProgramEnrollmentService
from app.services.secretariat.events import EnrollmentEventRecorder
from app.services.secretariat.internal_transfer import InternalTransferService
from app.services.secretariat.lifecycle import EnrollmentLifecycleService
from app.services.secretariat.reenrollment import ReenrollmentService

router = APIRouter(prefix="/enrollments/{enrollment_id}")


def _status_change(target: ProgramEnrollmentStatus):
    def change(
        enrollment_id: UUID,
        data: ReasonInput,
        db: Session = Depends(get_db),
        current: Student = Depends(get_current_secretariat),
    ):
        EnrollmentLifecycleService(db).transition(enrollment_id, target, current.id, reason=data.reason)
        return ProgramEnrollmentService(db).get_or_404(enrollment_id)
    return change


for path, target in (
    ("/lock", ProgramEnrollmentStatus.locked),
    ("/reactivate", ProgramEnrollmentStatus.active),
    ("/cancel", ProgramEnrollmentStatus.cancelled),
    ("/drop", ProgramEnrollmentStatus.dropped),
):
    router.add_api_route(path, _status_change(target), methods=["POST"], response_model=ProgramEnrollmentOut, name=f"enrollment_{path[1:]}")


@router.post("/transfer-out", response_model=ProgramEnrollmentOut)
def transfer_out(enrollment_id: UUID, data: TransferOutInput, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    EnrollmentLifecycleService(db).transfer_out(enrollment_id, data.destination, data.reason, current.id)
    return ProgramEnrollmentService(db).get_or_404(enrollment_id)


@router.post("/transfer-internal", response_model=ProgramEnrollmentOut, status_code=201)
def transfer_internal(
    enrollment_id: UUID,
    data: InternalTransferInput,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_secretariat),
):
    return InternalTransferService(db).transfer(enrollment_id, data.program_id, data.curriculum_id, data.reason, current.id)


@router.post("/change-curriculum", response_model=ProgramEnrollmentOut)
def change_curriculum(
    enrollment_id: UUID,
    data: CurriculumChangeInput,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_secretariat),
):
    EnrollmentLifecycleService(db).change_curriculum(enrollment_id, data.curriculum_id, data.reason, current.id)
    return ProgramEnrollmentService(db).get_or_404(enrollment_id)


@router.get("/registrations", response_model=list[TermRegistrationOut])
def list_registrations(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ReenrollmentService(db).list(enrollment_id)


@router.post("/registrations", response_model=TermRegistrationOut, status_code=201)
def reenroll(enrollment_id: UUID, data: ReenrollInput, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return ReenrollmentService(db).reenroll(enrollment_id, data, current.id)


@router.get("/events", response_model=list[EnrollmentEventOut])
def list_events(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    EnrollmentLifecycleService(db).get_or_404(enrollment_id)
    return EnrollmentEventRecorder(db).list(enrollment_id)


@router.get("", response_model=ProgramEnrollmentOut)
def get_enrollment(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ProgramEnrollmentService(db).get_or_404(enrollment_id)
