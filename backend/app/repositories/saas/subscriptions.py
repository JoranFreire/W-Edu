from __future__ import annotations
from uuid import UUID

from app.models.institution import InstitutionMembership
from app.models.saas import InstitutionSubscription
from app.models.student import UserRole
from app.repositories.academic._base import Repository


class InstitutionSubscriptionRepository(Repository[InstitutionSubscription]):
    model = InstitutionSubscription

    def get_for(self, institution_id: UUID) -> InstitutionSubscription | None:
        return self.db.query(InstitutionSubscription).filter(InstitutionSubscription.institution_id == institution_id).first()

    def active_students(self, institution_id: UUID) -> int:
        return (
            self.db.query(InstitutionMembership.id)
            .filter(
                InstitutionMembership.institution_id == institution_id,
                InstitutionMembership.role == UserRole.student,
                InstitutionMembership.is_active.is_(True),
            )
            .count()
        )
