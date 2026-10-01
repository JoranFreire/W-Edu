from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models.institution import InstitutionMembership, MemberRole
from app.models.student import UserRole


class MemberRoleRepository:
    """Papeis das pessoas por instituicao (o principal fica no vinculo; os demais, em `institution_member_roles`)."""

    def __init__(self, db: Session):
        self.db = db

    def roles_of(self, institution_id: UUID, user_id: UUID) -> frozenset[UserRole]:
        membership = self._membership(institution_id, user_id)
        return membership.roles if membership and membership.is_active else frozenset()

    def roles_by_user(self, institution_id: UUID, user_ids: Iterable[UUID]) -> dict[UUID, frozenset[UserRole]]:
        ids = list(user_ids)
        if not ids:
            return {}
        memberships = (
            self.db.query(InstitutionMembership)
            .filter(InstitutionMembership.institution_id == institution_id, InstitutionMembership.user_id.in_(ids))
            .all()
        )
        return {membership.user_id: membership.roles for membership in memberships if membership.is_active}

    def user_ids_with_role(self, institution_id: UUID, roles: Iterable[UserRole]) -> Select:
        """Subconsulta dos ids de quem tem algum dos papeis na instituicao (para filtrar `Student.id.in_(...)`)."""
        wanted = list(roles)
        extra = select(MemberRole.membership_id).where(MemberRole.role.in_(wanted))
        return (
            select(InstitutionMembership.user_id)
            .where(InstitutionMembership.institution_id == institution_id, InstitutionMembership.is_active.is_(True))
            .where(or_(InstitutionMembership.role.in_(wanted), InstitutionMembership.id.in_(extra)))
        )

    def set_roles(self, membership: InstitutionMembership, primary: UserRole, roles: Iterable[UserRole]) -> None:
        """Define o papel principal e os demais; o principal sempre faz parte do conjunto."""
        wanted = set(roles) | {primary}
        membership.role = primary
        for item in list(membership.member_roles):
            if item.role not in wanted:
                membership.member_roles.remove(item)
        current = {item.role for item in membership.member_roles}
        for role in sorted(wanted - current, key=lambda value: value.value):
            membership.member_roles.append(MemberRole(role=role))

    def _membership(self, institution_id: UUID, user_id: UUID) -> InstitutionMembership | None:
        return (
            self.db.query(InstitutionMembership)
            .filter(InstitutionMembership.institution_id == institution_id, InstitutionMembership.user_id == user_id)
            .first()
        )
