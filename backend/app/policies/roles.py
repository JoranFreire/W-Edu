"""Papeis da pessoa na instituicao ativa: uma pessoa pode acumular varios (aluno e professor, por exemplo).

Quem faz a requisicao tem `active_roles` carregado na autenticacao. Para outras pessoas (o instrutor de uma
turma, o aluno de uma ocorrencia), os papeis sao lidos sob demanda na instituicao da sessao e guardados no
objeto. Sem sessao nem instituicao (usuarios montados em testes), vale o papel principal (`users.role`).
"""

from collections.abc import Iterable

from sqlalchemy import inspect

from app.core.tenancy import bound_institution_id
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.repositories.member_roles import MemberRoleRepository


def _load(user: Student) -> frozenset[UserRole] | None:
    state = inspect(user, raiseerr=False)
    session = state.session if state is not None else None
    institution_id = bound_institution_id(session) if session else None
    if institution_id is None:
        return None
    roles = MemberRoleRepository(session).roles_of(institution_id, user.id)
    return roles | {UserRole.super_admin} if user.role == UserRole.super_admin else roles


def roles_of(user: Student) -> frozenset[UserRole]:
    roles = getattr(user, "active_roles", None)
    if roles is None:
        roles = _load(user)
        if roles is not None:
            user.active_roles = roles
    return roles or frozenset({user.role})


def has_role(user: Student, *roles: UserRole) -> bool:
    return not roles_of(user).isdisjoint(roles)


def has_any_role(user: Student, roles: Iterable[UserRole]) -> bool:
    return not roles_of(user).isdisjoint(roles)


def is_admin(user: Student) -> bool:
    return has_any_role(user, ADMIN_ROLES)


def is_super_admin(user: Student) -> bool:
    """Administracao da plataforma: papel global da conta, nao de uma instituicao."""
    return user.role == UserRole.super_admin


def can_receive_profiles(user: Student) -> bool:
    """Perfis de acesso valem para quem atua na instituicao: nao para a plataforma nem para quem so e responsavel."""
    return not is_super_admin(user) and roles_of(user) != frozenset({UserRole.guardian})


def forget_roles(user: Student) -> None:
    """Descarta os papeis guardados (depois de altera-los na mesma requisicao)."""
    if hasattr(user, "active_roles"):
        del user.active_roles
