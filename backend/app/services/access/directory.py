from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.policies.permissions import effective_permissions
from app.policies.roles import can_receive_profiles
from app.repositories.student import StudentRepository
from app.schemas.access import BuiltInProfileOut, MemberOut, MyAccessOut, PermissionOut
from app.services.access.catalog import CATALOG, role_permissions
from app.services.people.roles import UserRoleService

# Papeis que recebem perfis (plataforma e responsavel ficam fora do RBAC da instituicao).
PROFILE_ROLES = [r for r in UserRole if r not in (UserRole.super_admin, UserRole.guardian, UserRole.admin)]


class AccessDirectory:
    """Catalogo, perfis padrao dos papeis, membros elegiveis e as permissoes do proprio usuario."""

    def __init__(self, db: Session):
        self.db = db
        self.users = StudentRepository(db)

    @staticmethod
    def catalog() -> list[PermissionOut]:
        return [PermissionOut(**permission.__dict__) for permission in CATALOG]

    @staticmethod
    def built_in() -> list[BuiltInProfileOut]:
        return [BuiltInProfileOut(role=role, permissions=sorted(role_permissions(role))) for role in PROFILE_ROLES]

    def members(self) -> list[MemberOut]:
        """Membros da instituicao ativa (o filtro do tenant restringe os usuarios)."""
        users = UserRoleService(self.db).load_many(self.users.list_all())
        return [
            MemberOut(id=user.id, name=user.name, email=user.email, role=user.role, roles=user.roles)
            for user in sorted(users, key=lambda u: u.name)
            if user.is_active and can_receive_profiles(user)
        ]

    @staticmethod
    def mine(user: Student) -> MyAccessOut:
        return MyAccessOut(role=user.role, roles=user.roles, permissions=sorted(effective_permissions(user)))
