from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_finance_staff, get_current_student
from app.models.student import Student
from app.schemas.finance import ChargeOut
from app.schemas.tuition import SettleInput, SettlementOut, TuitionChargeOut
from app.services.tuition.settlement import TuitionSettlementService
from app.services.tuition.statements import TuitionStatementService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/charges", response_model=list[TuitionChargeOut])
def enrollment_statement(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_finance_staff)):
    return TuitionStatementService(db).for_enrollment(enrollment_id)


@router.get("/my/charges", response_model=list[TuitionChargeOut])
def my_statement(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return TuitionStatementService(db).for_user(current)


@router.get("/charges/{charge_id}/quote", response_model=SettlementOut)
def quote_charge(charge_id: UUID, on: date | None = None, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return TuitionStatementService(db).quote_for(current, charge_id, on)


@router.post("/charges/{charge_id}/settle", response_model=ChargeOut)
def settle_charge(charge_id: UUID, data: SettleInput, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return TuitionSettlementService(db).settle(charge_id, data.paid_on, data.payment_method)
