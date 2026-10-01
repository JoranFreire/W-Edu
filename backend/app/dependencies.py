from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_payload
from app.core.tenancy import bind_institution
from app.core.tenant_host import slug_from_host
from app.models.institution import Institution
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.repositories.student import StudentRepository
from app.services.tenant_access import TenantAccessService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

INSTITUTION_HEADER = "X-Institution"


def _authenticate(token: str, db: Session) -> tuple[Student, dict]:
    payload = decode_access_payload(token)
    student_id = payload.get("sub") if payload else None
    if not student_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    student = StudentRepository(db).get_by_id(int(student_id))
    if not student or not student.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return student, payload


def requested_institution_ref(request: Request) -> str | None:
    """Instituicao pedida explicitamente pela requisicao: header `X-Institution` ou subdominio."""
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    return request.headers.get(INSTITUTION_HEADER) or slug_from_host(host)


def _activate_institution(request: Request, db: Session, student: Student, payload: dict) -> None:
    """Resolve a instituicao (header, subdominio ou token) e vincula a sessao do banco."""
    requested = requested_institution_ref(request) or payload.get("inst")
    institution = TenantAccessService(db).resolve_for_user(student, requested)
    bind_institution(db, institution.id)
    request.state.institution = institution


def get_current_student(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Student:
    student, payload = _authenticate(token, db)
    _activate_institution(request, db, student, payload)
    return student


get_current_user = get_current_student


def get_current_institution(request: Request, _: Student = Depends(get_current_student)) -> Institution:
    return request.state.institution


def get_current_super_admin(current: Student = Depends(get_current_student)) -> Student:
    if current.role != UserRole.super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito à administração da plataforma")
    return current


def get_current_admin(current: Student = Depends(get_current_student)) -> Student:
    if current.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    return current


def get_current_admin_or_coordinator(current: Student = Depends(get_current_student)) -> Student:
    if current.role not in ADMIN_ROLES | {UserRole.coordinator}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores e coordenadores")
    return current


def get_current_teaching_staff(current: Student = Depends(get_current_student)) -> Student:
    """Quem lanca notas e diario: administradores, coordenadores e instrutores (escopo por oferta na policy)."""
    if current.role not in ADMIN_ROLES | {UserRole.coordinator, UserRole.instructor}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a docentes e coordenação")
    return current


def get_current_secretariat(current: Student = Depends(get_current_student)) -> Student:
    """Secretaria academica: administradores, coordenadores e secretarios."""
    if current.role not in ADMIN_ROLES | {UserRole.coordinator, UserRole.secretary}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito à secretaria")
    return current


def get_current_guardian(current: Student = Depends(get_current_student)) -> Student:
    """Portal do responsavel."""
    if current.role != UserRole.guardian:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a responsáveis")
    return current


def get_current_academic_staff(current: Student = Depends(get_current_student)) -> Student:
    if current.role not in ADMIN_ROLES | {UserRole.coordinator, UserRole.company_manager}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito")
    if current.role == UserRole.company_manager and current.organization_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gestor sem empresa vinculada")
    return current


def get_current_admin_or_company_manager(current: Student = Depends(get_current_student)) -> Student:
    if current.role not in ADMIN_ROLES | {UserRole.company_manager}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito")
    if current.role == UserRole.company_manager and current.organization_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gestor sem empresa vinculada")
    return current


def ensure_super_admin_boundary(current: Student, role: UserRole | None = None, target: Student | None = None) -> None:
    """Somente super admin atribui o papel super_admin ou altera um super admin."""
    if current.role == UserRole.super_admin:
        return
    if role == UserRole.super_admin or (target is not None and target.role == UserRole.super_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operação restrita à administração da plataforma")
