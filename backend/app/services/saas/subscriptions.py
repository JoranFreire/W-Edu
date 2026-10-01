from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.saas import InstitutionSubscription
from app.repositories.saas import InstitutionSubscriptionRepository
from app.schemas.saas import SubscriptionInput
from app.services.academic.errors import conflict, not_found
from app.services.institution import InstitutionService
from app.services.saas.plans import SaasPlanService


class InstitutionSubscriptionService:
    """Plano contratado por instituicao: o super admin atribui, troca ou cancela."""

    def __init__(self, db: Session):
        self.repo = InstitutionSubscriptionRepository(db)
        self.plans = SaasPlanService(db)
        self.institutions = InstitutionService(db)

    def get(self, institution_id: int) -> InstitutionSubscription | None:
        return self.repo.get_for(institution_id)

    def get_or_404(self, institution_id: int) -> InstitutionSubscription:
        subscription = self.repo.get_for(institution_id)
        if not subscription:
            raise not_found("Instituição sem plano contratado")
        return subscription

    def set(self, institution_id: int, data: SubscriptionInput) -> InstitutionSubscription:
        self.institutions.get_or_404(institution_id)
        plan = self.plans.get_or_404(data.plan_id)
        if not plan.is_active:
            raise conflict("Plano inativo")
        subscription = self.repo.get_for(institution_id) or InstitutionSubscription(
            institution_id=institution_id, started_on=data.started_on or date.today()
        )
        subscription.plan_id, subscription.status, subscription.trial_ends_on = plan.id, data.status, data.trial_ends_on
        if data.started_on:
            subscription.started_on = data.started_on
        saved = self.repo.save(subscription)
        self.repo.db.refresh(saved, ["plan"])
        return saved
