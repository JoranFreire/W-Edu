from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.policies.permissions import effective_permissions
from app.repositories.student import StudentRepository
from app.schemas.access import BuiltInProfileOut, MemberOut, MyAccessOut, PermissionOut
from app.services.access.catalog import CATALOG, role_permissions

# Papeis que recebem perfis (plataforma e responsavel ficam fora do RBAC da instituicao).
PROFILE_ROLES = [r for r in UserRole if r not in (UserRole.super_admin, UserRole.guardian, UserRole.admin)]


class AccessDirectory:
    """Catalogo, perfis padrao dos papeis, membros elegiveis e as permissoes do proprio usuario."""

    def __init__(self, db: Session):
        self.users = StudentRepository(db)

    @staticmethod
    def catalog() -> list[PermissionOut]:
        return [PermissionOut(**permission.__dict__) for permission in CATALOG]

    @staticmethod
    def built_in() -> list[BuiltInProfileOut]:
        return [BuiltInProfileOut(role=role, permissions=sorted(role_permissions(role))) for role in PROFILE_ROLES]

    def members(self) -> list[MemberOut]:
        """Membros da instituicao ativa (o filtro do tenant restringe os usuarios)."""
        return [
            MemberOut(id=user.id, name=user.name, email=user.email, role=user.role)
            for user in sorted(self.users.list_all(), key=lambda u: u.name)
            if user.is_active and user.role not in (UserRole.super_admin, UserRole.guardian)
        ]

    @staticmethod
    def mine(user: Student) -> MyAccessOut:
        return MyAccessOut(role=user.role, permissions=sorted(effective_permissions(user)))
