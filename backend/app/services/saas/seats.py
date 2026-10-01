from __future__ import annotations
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.saas import SaasSubscriptionStatus
from app.repositories.saas import InstitutionSubscriptionRepository
from app.schemas.saas import UsageOut


class StudentSeatPolicy:
    """Limite de alunos ativos do plano contratado (sem plano ou sem limite, nao bloqueia)."""

    def __init__(self, db: Session):
        self.subscriptions = InstitutionSubscriptionRepository(db)

    def usage(self, institution_id: UUID) -> UsageOut:
        subscription = self.subscriptions.get_for(institution_id)
        limit = subscription.plan.max_students if subscription and subscription.status != SaasSubscriptionStatus.cancelled else None
        return UsageOut(active_students=self.subscriptions.active_students(institution_id), max_students=limit)

    def ensure_available(self, institution_id: UUID) -> None:
        usage = self.usage(institution_id)
        if usage.max_students is not None and usage.active_students >= usage.max_students:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Limite de alunos do plano contratado atingido")
