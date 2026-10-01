from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin
from app.models.student import Student
from app.schemas.tuition import GenerationOut, TuitionPlanCreate, TuitionPlanOut, TuitionPlanUpdate
from app.services.tuition.billing import TuitionBillingService
from app.services.tuition.plans import TuitionPlanService

router = APIRouter(prefix="/plans")


@router.get("", response_model=list[TuitionPlanOut])
def list_plans(term_id: int | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return TuitionPlanService(db).list(term_id)


@router.post("", response_model=TuitionPlanOut, status_code=201)
def create_plan(data: TuitionPlanCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return TuitionPlanService(db).create(data)


@router.patch("/{plan_id}", response_model=TuitionPlanOut)
def update_plan(plan_id: int, data: TuitionPlanUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return TuitionPlanService(db).update(plan_id, data)


@router.post("/{plan_id}/generate", response_model=GenerationOut)
def generate_charges(plan_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return TuitionBillingService(db).generate(plan_id)
