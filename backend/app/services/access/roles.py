from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.access import AccessRole, AccessRoleAssignment
from app.models.student import Student, UserRole
from app.policies.permissions import effective_permissions
from app.policies.roles import can_receive_profiles
from app.repositories.access import AccessRoleRepository
from app.repositories.student import StudentRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.access import AccessRoleInput, AccessRoleOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.access.catalog import KEYS


def to_out(role: AccessRole) -> AccessRoleOut:
    return AccessRoleOut(
        id=role.id, name=role.name, description=role.description, permissions=sorted(role.permissions or []),
        members=[PersonSummary.model_validate(a.user) for a in sorted(role.assignments, key=lambda a: a.user.name)],
    )


class AccessRoleService:
    """Perfis personalizados: so se concede permissao que quem concede ja tem (sem escalada de privilegio)."""

    def __init__(self, db: Session):
        self.repo = AccessRoleRepository(db)
        self.users = StudentRepository(db)

    def list(self) -> list[AccessRoleOut]:
        return [to_out(role) for role in self.repo.list()]

    def create(self, data: AccessRoleInput, actor: Student) -> AccessRoleOut:
        if self.repo.get_by_name(data.name):
            raise conflict("Já existe perfil com este nome")
        permissions = self._grantable(data.permissions, actor)
        role = self.repo.save(AccessRole(name=data.name, description=data.description, permissions=permissions))
        return to_out(role)

    def update(self, role_id: UUID, data: AccessRoleInput, actor: Student) -> AccessRoleOut:
        role = self._get_or_404(role_id)
        if data.name != role.name and self.repo.get_by_name(data.name):
            raise conflict("Já existe perfil com este nome")
        # Quem nao tem uma permissao do perfil nao pode tira-la nem altera-lo.
        self._grantable(role.permissions or [], actor)
        role.name, role.description, role.permissions = data.name, data.description, self._grantable(data.permissions, actor)
        return to_out(self.repo.save(role))

    def delete(self, role_id: UUID, actor: Student) -> None:
        role = self._get_or_404(role_id)
        self._grantable(role.permissions or [], actor)
        self.repo.delete(role)

    def assign(self, role_id: UUID, user_id: UUID, actor: Student) -> AccessRoleOut:
        role = self._get_or_404(role_id)
        self._grantable(role.permissions or [], actor)
        user = self.users.get_by_id(user_id)
        if not user or not can_receive_profiles(user):
            raise not_found("Usuário não encontrado")
        if not self.repo.assignment(role.id, user.id):
            self.repo.add(AccessRoleAssignment(role_id=role.id, user_id=user.id))
            self.repo.commit()
        self.repo.db.refresh(role)
        return to_out(role)

    def unassign(self, role_id: UUID, user_id: UUID, actor: Student) -> AccessRoleOut:
        role = self._get_or_404(role_id)
        self._grantable(role.permissions or [], actor)
        assignment = self.repo.assignment(role.id, user_id)
        if not assignment:
            raise not_found("Usuário não tem este perfil")
        self.repo.delete(assignment)
        self.repo.db.refresh(role)
        return to_out(role)

    @staticmethod
    def _grantable(permissions: list[str], actor: Student) -> list[str]:
        unknown = set(permissions) - KEYS
        if unknown:
            raise bad_request(f"Permissões desconhecidas: {', '.join(sorted(unknown))}")
        missing = set(permissions) - effective_permissions(actor)
        if missing:
            raise conflict(f"Você não pode conceder permissões que não tem: {', '.join(sorted(missing))}")
        return sorted(set(permissions))

    def _get_or_404(self, role_id: UUID) -> AccessRole:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise not_found("Perfil não encontrado")
        return role
