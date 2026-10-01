from __future__ import annotations
from uuid import UUID

from sqlalchemy import func

from app.models.saas import InstitutionSubscription
from app.models.student import UserRole
from app.repositories.academic._base import Repository
from app.repositories.member_roles import MemberRoleRepository


class InstitutionSubscriptionRepository(Repository[InstitutionSubscription]):
    model = InstitutionSubscription

    def get_for(self, institution_id: UUID) -> InstitutionSubscription | None:
        return self.db.query(InstitutionSubscription).filter(InstitutionSubscription.institution_id == institution_id).first()

    def active_students(self, institution_id: UUID) -> int:
        # Alunos ativos da instituicao, inclusive quem tambem tem outro papel nela.
        students = MemberRoleRepository(self.db).user_ids_with_role(institution_id, [UserRole.student]).subquery()
        return self.db.query(func.count()).select_from(students).scalar() or 0
