from uuid import UUID

from sqlalchemy.orm import Session

from app.core.tenancy import bound_institution_id
from app.models.student import Student, UserRole
from app.repositories.member_roles import MemberRoleRepository


class UserRoleService:
    """Carrega de uma vez os papeis na instituicao (quem faz a requisicao, ou uma lista de pessoas)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = MemberRoleRepository(db)

    def load(self, user: Student, institution_id: UUID | None = None) -> Student:
        institution_id = institution_id or bound_institution_id(self.db)
        roles = self.repo.roles_of(institution_id, user.id) if institution_id else frozenset()
        user.active_roles = roles | {UserRole.super_admin} if user.role == UserRole.super_admin else roles
        return user

    def load_many(self, users: list[Student]) -> list[Student]:
        institution_id = bound_institution_id(self.db)
        by_user = self.repo.roles_by_user(institution_id, [user.id for user in users]) if institution_id else {}
        for user in users:
            roles = by_user.get(user.id, frozenset())
            user.active_roles = roles | {UserRole.super_admin} if user.role == UserRole.super_admin else roles
        return users
