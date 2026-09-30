from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.institution import MembershipOut, SwitchInstitutionRequest
from app.services.auth import AuthService
from app.services.institution import InstitutionService

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token, institution = AuthService(db).login(data.email, data.password, data.institution)
    return TokenOut(access_token=token, institution=institution)


@router.get("/institutions", response_model=list[MembershipOut])
def my_institutions(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return InstitutionService(db).list_memberships(current)


@router.post("/switch-institution", response_model=TokenOut)
def switch_institution(
    data: SwitchInstitutionRequest,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    service = InstitutionService(db)
    institution = service.resolve_for_user(current, data.institution)
    return TokenOut(access_token=service.issue_token(current, institution), institution=institution)
