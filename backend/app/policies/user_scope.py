from uuid import UUID

from fastapi import HTTPException, status

from app.models.student import ADMIN_ROLES, InstructorAvailability, Student, UserRole
from app.services.student import StudentService
from app.policies.roles import has_any_role, has_role, roles_of

MANAGEABLE_ACADEMIC_ROLES = {UserRole.student, UserRole.instructor}
PRIVILEGED_ROLES = ADMIN_ROLES | {UserRole.coordinator, UserRole.company_manager, UserRole.secretary}


def ensure_academic_user_scope(current: Student, target: Student) -> None:
    """Coordenacao e gestores so gerem alunos/instrutores; gestores, apenas da propria empresa."""
    if has_any_role(current, ADMIN_ROLES):
        return
    if has_role(current, UserRole.company_manager) and target.organization_id != current.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário fora da empresa")
    # Quem acumula um papel fora do escopo (ex.: aluno que tambem e secretaria) so e gerido pela administracao.
    if not roles_of(target) <= MANAGEABLE_ACADEMIC_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil fora do escopo")


def requested_roles(role: UserRole | None, roles: list[UserRole] | None) -> set[UserRole]:
    """Papeis que uma criacao/edicao de usuario pede (o principal e a lista)."""
    return {item for item in (role, *(roles or [])) if item is not None}


def ensure_can_assign_roles(current: Student, requested: set[UserRole]) -> None:
    """Coordenacao e gestor de empresa so atribuem papeis academicos; a administracao atribui qualquer um."""
    if has_any_role(current, ADMIN_ROLES):
        return
    if requested & PRIVILEGED_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão para atribuir este papel")


def ensure_can_view_user(current: Student, target: Student) -> None:
    """Consulta (dossie): a equipe ve qualquer pessoa da instituicao; gestor de empresa, so a propria empresa."""
    if has_role(current, UserRole.company_manager) and target.organization_id != current.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário fora da empresa")


def ensure_availability_scope(current: Student, service: StudentService, availability_id: UUID) -> InstructorAvailability:
    availability = service.availability_repo.get_by_id(availability_id)
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disponibilidade não encontrada")
    instructor = service.get_or_404(availability.instructor_profile.student_id)
    ensure_academic_user_scope(current, instructor)
    return availability
