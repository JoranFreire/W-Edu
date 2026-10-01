from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_student, get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import OfferingResultsOut, PeriodClosureOut, RecoveryInput, ReportCardEntry
from app.services.assessment import FinalResultService, PeriodClosureService, ReportCardService

router = APIRouter()


@router.post("/offerings/{offering_id}/periods/{period_id}/close", response_model=PeriodClosureOut)
def close_period(offering_id: UUID, period_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return PeriodClosureService(db).close(offering_id, period_id, current)


@router.delete("/offerings/{offering_id}/periods/{period_id}/close", status_code=204)
def reopen_period(offering_id: UUID, period_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_admin_or_coordinator)):
    PeriodClosureService(db).reopen(offering_id, period_id, current)


@router.get("/offerings/{offering_id}/results", response_model=OfferingResultsOut)
def get_results(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return FinalResultService(db).overview(offering_id, current)


@router.post("/offerings/{offering_id}/results/compute", response_model=OfferingResultsOut)
def compute_results(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return FinalResultService(db).compute(offering_id, current)


@router.put("/offerings/{offering_id}/recovery", response_model=OfferingResultsOut)
def save_recovery(
    offering_id: UUID,
    data: list[RecoveryInput],
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_teaching_staff),
):
    return FinalResultService(db).save_recovery(offering_id, data, current)


@router.post("/offerings/{offering_id}/finalize", response_model=OfferingResultsOut)
def finalize_offering(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_admin_or_coordinator)):
    return FinalResultService(db).finalize(offering_id, current)


@router.get("/my/report-card", response_model=list[ReportCardEntry])
def my_report_card(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ReportCardService(db).for_student(current)
