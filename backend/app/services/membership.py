from uuid import UUID

from sqlalchemy.orm import Session

from app.models.institution import InstitutionMembership
from app.models.student import Student
from app.repositories.institution import MembershipRepository


class MembershipService:
    """Vinculos usuario-instituicao."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)

    def list_active(self, user: Student) -> list[InstitutionMembership]:
        return self.repo.list_active_for_user(user.id)

    def get(self, institution_id: UUID, user_id: UUID) -> InstitutionMembership | None:
        return self.repo.get(institution_id, user_id)

    def add_member(self, institution_id: UUID, user: Student) -> InstitutionMembership:
        membership = self.repo.get(institution_id, user.id)
        if membership:
            membership.role = user.role
            membership.is_active = True
            return membership
        return self.repo.add(InstitutionMembership(institution_id=institution_id, user_id=user.id, role=user.role))

    def sync_member_role(self, institution_id: UUID, user: Student) -> None:
        membership = self.repo.get(institution_id, user.id)
        if membership:
            membership.role = user.role
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
