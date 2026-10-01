from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.ids import parse_id
from app.core.security import decode_access_payload
from app.core.tenancy import bind_institution
from app.core.tenant_host import slug_from_host
from app.models.institution import Institution
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.policies.permissions import ensure_any_permission, ensure_permission
from app.repositories.access import AccessRoleRepository
from app.repositories.student import StudentRepository
from app.services.institution import InstitutionService
from app.services.people.roles import UserRoleService
from app.services.public_site.domains import InstitutionDomainService
from app.services.tenant_access import TenantAccessService
from app.policies.roles import has_any_role, has_role, is_super_admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

INSTITUTION_HEADER = "X-Institution"


def _authenticate(token: str, db: Session) -> tuple[Student, dict]:
    payload = decode_access_payload(token)
    student_id = payload.get("sub") if payload else None
    if not student_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user_id = parse_id(student_id)
    student = StudentRepository(db).get_by_id(user_id) if user_id else None
    if not student or not student.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return student, payload


def requested_institution_ref(request: Request) -> str | None:
    """Instituicao pedida explicitamente pela requisicao: header `X-Institution` ou subdominio."""
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    return request.headers.get(INSTITUTION_HEADER) or slug_from_host(host)


def request_institution_ref(request: Request, db: Session) -> str | None:
    """Instituicao pedida: header `X-Institution`, subdominio ou dominio proprio do cliente (ex.: escola.com.br)."""
    explicit = requested_institution_ref(request)
    if explicit:
        return explicit
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    return InstitutionDomainService(db).ref_for_host(host)


def _activate_institution(request: Request, db: Session, student: Student, payload: dict) -> None:
    """Resolve a instituicao (header, subdominio, dominio proprio ou token) e vincula a sessao do banco."""
    requested = request_institution_ref(request, db) or payload.get("inst")
    institution = TenantAccessService(db).resolve_for_user(student, requested)
    bind_institution(db, institution.id)
    request.state.institution = institution
    # Papeis da pessoa nesta instituicao (pode acumular varios) e perfis de acesso que somam permissoes (RBAC).
    UserRoleService(db).load(student, institution.id)
    student.granted_permissions = AccessRoleRepository(db).permissions_of(student.id)


def get_public_institution(request: Request, db: Session = Depends(get_db)) -> Institution:
    """Rotas publicas por instituicao (catalogo de editais): header, subdominio, dominio proprio ou `?institution=`."""
    ref = request_institution_ref(request, db) or request.query_params.get("institution")
    institution = InstitutionService(db).get_public(ref)
    bind_institution(db, institution.id)
    return institution


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
    if not is_super_admin(current):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito à administração da plataforma")
    return current


def get_current_admin(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `institution.manage` (administradores, ou perfil que a conceda)."""
    return ensure_permission(current, "institution.manage", "Acesso restrito a administradores")


def get_current_admin_or_coordinator(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `academic.manage` (administradores e coordenadores, ou perfil que a conceda)."""
    return ensure_permission(current, "academic.manage", "Acesso restrito a administradores e coordenadores")


def get_current_teaching_staff(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `teaching.access`: quem lanca notas e diario (escopo por oferta na policy)."""
    return ensure_permission(current, "teaching.access", "Acesso restrito a docentes e coordenação")


def get_current_secretariat(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `secretariat.access`: secretaria academica."""
    return ensure_permission(current, "secretariat.access", "Acesso restrito à secretaria")


def get_current_school_staff(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `school_life.access`: equipe escolar (ocorrencias, agenda, frequencia e beneficios)."""
    return ensure_permission(current, "school_life.access", "Acesso restrito à equipe escolar")


def get_current_finance_staff(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `finance.access`: financeiro educacional."""
    return ensure_permission(current, "finance.access", "Acesso restrito ao financeiro")


def get_current_access_manager(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `access.manage`: perfis de acesso da instituicao."""
    return ensure_permission(current, "access.manage", "Acesso restrito à gestão de perfis")


def get_current_warehouse_requester(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `warehouse.request`: quem pede materiais ao almoxarifado."""
    return ensure_permission(current, "warehouse.request", "Sem permissão para requisitar materiais")


def get_current_warehouse_manager(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `warehouse.manage`: quem opera o almoxarifado."""
    return ensure_permission(current, "warehouse.manage", "Acesso restrito ao almoxarifado")


def get_current_warehouse_reader(current: Student = Depends(get_current_student)) -> Student:
    """Permissao `warehouse.reports`: relatorios do almoxarifado."""
    return ensure_permission(current, "warehouse.reports", "Sem permissão para relatórios do almoxarifado")


def get_current_warehouse_user(current: Student = Depends(get_current_student)) -> Student:
    """Qualquer permissao do almoxarifado: ver o catalogo de materiais e o saldo."""
    return ensure_any_permission(current, ("warehouse.request", "warehouse.manage", "warehouse.reports"), "Acesso restrito ao almoxarifado")


def get_current_guardian(current: Student = Depends(get_current_student)) -> Student:
    """Portal do responsavel."""
    if not has_role(current, UserRole.guardian):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a responsáveis")
    return current


def get_current_academic_staff(current: Student = Depends(get_current_student)) -> Student:
    if not has_any_role(current, ADMIN_ROLES | {UserRole.coordinator, UserRole.company_manager}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito")
    if has_role(current, UserRole.company_manager) and current.organization_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gestor sem empresa vinculada")
    return current


def get_current_admin_or_company_manager(current: Student = Depends(get_current_student)) -> Student:
    if not has_any_role(current, ADMIN_ROLES | {UserRole.company_manager}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito")
    if has_role(current, UserRole.company_manager) and current.organization_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gestor sem empresa vinculada")
    return current


def ensure_super_admin_boundary(current: Student, role: UserRole | None = None, target: Student | None = None,
                                roles: list[UserRole] | None = None) -> None:
    """Somente super admin atribui o papel super_admin (como principal ou na lista de papeis) ou altera um super admin."""
    if is_super_admin(current):
        return
    requested = {role, *(roles or [])}
    if UserRole.super_admin in requested or (target is not None and target.role == UserRole.super_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operação restrita à administração da plataforma")
