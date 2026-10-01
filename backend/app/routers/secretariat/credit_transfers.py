from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_secretariat
from app.models.student import Student
from app.schemas.secretariat import CreditTransferCreate, CreditTransferDecision, CreditTransferOut
from app.services.secretariat.credit_transfers import CreditTransferService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/credit-transfers", response_model=list[CreditTransferOut])
def list_credit_transfers(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return CreditTransferService(db).list(enrollment_id)


@router.post("/enrollments/{enrollment_id}/credit-transfers", response_model=CreditTransferOut, status_code=201)
def request_credit_transfer(
    enrollment_id: UUID,
    data: CreditTransferCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_secretariat),
):
    return CreditTransferService(db).request(enrollment_id, data)


@router.post("/credit-transfers/{transfer_id}/decision", response_model=CreditTransferOut)
def decide_credit_transfer(
    transfer_id: UUID,
    data: CreditTransferDecision,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_admin_or_coordinator),
):
    return CreditTransferService(db).decide(transfer_id, data, current.id)
