from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_benefit_validator, get_current_school_staff, get_current_student
from app.models.student import Student
from app.schemas.benefit_vouchers import IndividualVoucherInput, VoucherBatchInput, VoucherBatchOut, RedeemInput, VoucherOut
from app.services.social.student_vouchers import StudentVoucherService
from app.services.social.voucher_redemption import VoucherRedemptionService
from app.services.social.voucher_release import VoucherReleaseService

router = APIRouter()


@router.post("/meetings/{meeting_id}/vouchers", response_model=VoucherBatchOut)
def release_in_meeting(meeting_id: UUID, data: VoucherBatchInput, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return VoucherReleaseService(db).release_in_meeting(meeting_id, data, current)


@router.post("/offerings/{offering_id}/vouchers", response_model=VoucherBatchOut)
def release_to_offering(offering_id: UUID, data: VoucherBatchInput, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return VoucherReleaseService(db).release_to_offering(offering_id, data, current)


@router.post("/vouchers", response_model=VoucherOut, status_code=201)
def release_to_student(data: IndividualVoucherInput, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return VoucherReleaseService(db).release_to_student(data, current)


@router.get("/offerings/{offering_id}/vouchers", response_model=list[VoucherOut])
def offering_vouchers(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return VoucherReleaseService(db).list_for_offering(offering_id, current)


@router.post("/vouchers/{voucher_id}/cancel", response_model=VoucherOut)
def cancel_voucher(voucher_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return VoucherReleaseService(db).cancel(voucher_id, current)


@router.post("/vouchers/lookup", response_model=VoucherOut)
def lookup_voucher(data: RedeemInput, db: Session = Depends(get_db), _: Student = Depends(get_current_benefit_validator)):
    # POST: o codigo do QR nao vai para a URL (logs de acesso).
    return VoucherRedemptionService(db).lookup(data.code)


@router.post("/vouchers/redeem", response_model=VoucherOut)
def redeem_voucher(data: RedeemInput, db: Session = Depends(get_db), current: Student = Depends(get_current_benefit_validator)):
    return VoucherRedemptionService(db).redeem(data.code, current)


@router.get("/my/vouchers", response_model=list[VoucherOut])
def my_vouchers(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return StudentVoucherService(db).for_student(current.id)
