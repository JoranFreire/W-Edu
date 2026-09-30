from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student, requested_institution_ref
from app.models.student import Student
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.institution import MembershipOut, SwitchInstitutionRequest
from app.services.auth import AuthService
from app.services.membership import MembershipService
from app.services.tenant_access import TenantAccessService

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
    institution_ref: str | None = Depends(requested_institution_ref),
):
    token, institution = AuthService(db).login(data.email, data.password, data.institution or institution_ref)
    return TokenOut(access_token=token, institution=institution)


@router.get("/institutions", response_model=list[MembershipOut])
def my_institutions(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return MembershipService(db).list_active(current)


@router.post("/switch-institution", response_model=TokenOut)
def switch_institution(
    data: SwitchInstitutionRequest,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    service = TenantAccessService(db)
    institution = service.resolve_for_user(current, data.institution)
    return TokenOut(access_token=service.issue_token(current, institution), institution=institution)
