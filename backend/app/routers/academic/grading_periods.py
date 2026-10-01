from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic_calendar import GradingPeriodCreate, GradingPeriodOut, GradingPeriodStatusChange, GradingPeriodUpdate
from app.services.academic import GradingPeriodService

router = APIRouter()


@router.get("/terms/{term_id}/grading-periods", response_model=list[GradingPeriodOut])
def list_grading_periods(term_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return GradingPeriodService(db).list(term_id)


@router.post("/terms/{term_id}/grading-periods", response_model=GradingPeriodOut, status_code=201)
def create_grading_period(
    term_id: UUID,
    data: GradingPeriodCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return GradingPeriodService(db).create(term_id, data)


@router.patch("/grading-periods/{period_id}", response_model=GradingPeriodOut)
def update_grading_period(
    period_id: UUID,
    data: GradingPeriodUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return GradingPeriodService(db).update(period_id, data)


@router.post("/grading-periods/{period_id}/status", response_model=GradingPeriodOut)
def change_grading_period_status(
    period_id: UUID,
    data: GradingPeriodStatusChange,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return GradingPeriodService(db).change_status(period_id, data.status)


@router.delete("/grading-periods/{period_id}", status_code=204)
def delete_grading_period(period_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    GradingPeriodService(db).delete(period_id)
