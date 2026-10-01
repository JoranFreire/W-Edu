from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import joinedload

from app.models.access import AccessRole, AccessRoleAssignment
from app.repositories.academic._base import Repository


class AccessRoleRepository(Repository[AccessRole]):
    model = AccessRole

    def list(self) -> list[AccessRole]:
        return (
            self.db.query(AccessRole)
            .options(joinedload(AccessRole.assignments).joinedload(AccessRoleAssignment.user))
            .order_by(AccessRole.name)
            .all()
        )

    def get_by_name(self, name: str) -> AccessRole | None:
        return self.db.query(AccessRole).filter(AccessRole.name == name).first()

    def permissions_of(self, user_id: UUID) -> frozenset[str]:
        """Permissoes somadas dos perfis do usuario na instituicao ativa (filtro do tenant)."""
        rows = (
            self.db.query(AccessRole.permissions)
            .join(AccessRoleAssignment, AccessRoleAssignment.role_id == AccessRole.id)
            .filter(AccessRoleAssignment.user_id == user_id)
            .all()
        )
        return frozenset(key for (permissions,) in rows for key in (permissions or []))

    def assignment(self, role_id: UUID, user_id: UUID) -> AccessRoleAssignment | None:
        return (
            self.db.query(AccessRoleAssignment)
            .filter(AccessRoleAssignment.role_id == role_id, AccessRoleAssignment.user_id == user_id)
            .first()
        )
