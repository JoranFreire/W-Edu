from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_institution
from app.models.institution import Institution
from app.models.student import Student
from app.schemas.saas import InstitutionPlanOut
from app.services.saas.overview import InstitutionPlanOverview

router = APIRouter()


@router.get("/current", response_model=InstitutionPlanOut)
def current_plan(
    db: Session = Depends(get_db), _: Student = Depends(get_current_admin), institution: Institution = Depends(get_current_institution),
):
    return InstitutionPlanOverview(db).for_institution(institution.id)
