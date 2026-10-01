from collections.abc import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.institution import InstitutionMembership
from app.models.student import Student, UserRole
from app.repositories.institution import MembershipRepository
from app.repositories.member_roles import MemberRoleRepository


class MembershipService:
    """Vinculos usuario-instituicao e os papeis da pessoa em cada uma."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)
        self.roles = MemberRoleRepository(db)

    def list_active(self, user: Student) -> list[InstitutionMembership]:
        return self.repo.list_active_for_user(user.id)

    def get(self, institution_id: UUID, user_id: UUID) -> InstitutionMembership | None:
        return self.repo.get(institution_id, user_id)

    def add_member(self, institution_id: UUID, user: Student, roles: Iterable[UserRole] | None = None) -> InstitutionMembership:
        """Vincula (ou reativa) a pessoa com o papel principal da conta e, se informados, os demais papeis."""
        membership = self.repo.get(institution_id, user.id)
        if membership is None:
            membership = self.repo.add(InstitutionMembership(institution_id=institution_id, user_id=user.id, role=user.role))
        membership.is_active = True
        self.roles.set_roles(membership, user.role, roles if roles is not None else membership.roles | {user.role})
        return membership

    def grant(self, institution_id: UUID, user: Student, role: UserRole) -> InstitutionMembership:
        """Acrescenta um papel sem tirar os que a pessoa ja tem (ex.: aluno que passa a ser responsavel)."""
        membership = self.repo.get(institution_id, user.id)
        if membership is None:
            membership = self.repo.add(InstitutionMembership(institution_id=institution_id, user_id=user.id, role=role))
        membership.is_active = True
        self.roles.set_roles(membership, membership.role, membership.roles | {role})
        return membership

    def set_roles(self, institution_id: UUID, user: Student, primary: UserRole, roles: Iterable[UserRole]) -> InstitutionMembership:
        membership = self.add_member(institution_id, user)
        self.roles.set_roles(membership, primary, roles)
        return membership

    def sync_member_role(self, institution_id: UUID, user: Student) -> None:
        """Papel principal e situacao da conta refletidos no vinculo (os demais papeis ficam)."""
        membership = self.repo.get(institution_id, user.id)
        if membership:
            self.roles.set_roles(membership, user.role, membership.roles | {user.role})
            membership.is_active = user.is_active

    def detach(self, institution_id: UUID | None, user: Student) -> bool:
        """Remove o vinculo com a instituicao ativa.

        Retorna True quando o usuario nao pertence a mais nenhuma instituicao
        (e pode ser excluido); nesse caso todos os vinculos sao removidos.
        """
        memberships = self.repo.list_all_for_user(user.id)
        remaining = [m for m in memberships if m.institution_id != institution_id]
        if institution_id is not None and remaining:
            for membership in memberships:
                if membership.institution_id == institution_id:
                    self.db.delete(membership)
            return False
        for membership in memberships:
            self.db.delete(membership)
        return True
