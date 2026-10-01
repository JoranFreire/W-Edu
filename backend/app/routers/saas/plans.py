from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_super_admin
from app.models.student import Student
from app.schemas.saas import SaasPlanCreate, SaasPlanOut, SaasPlanUpdate
from app.services.saas.plans import SaasPlanService

router = APIRouter(prefix="/plans")


@router.get("", response_model=list[SaasPlanOut])
def list_plans(db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return SaasPlanService(db).list()


@router.post("", response_model=SaasPlanOut, status_code=201)
def create_plan(data: SaasPlanCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return SaasPlanService(db).create(data)


@router.patch("/{plan_id}", response_model=SaasPlanOut)
def update_plan(plan_id: UUID, data: SaasPlanUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return SaasPlanService(db).update(plan_id, data)
