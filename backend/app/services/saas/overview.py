from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.saas import InstitutionPlanOut, PlatformInvoiceOut, SubscriptionOut
from app.services.saas.invoices import PlatformInvoiceService
from app.services.saas.seats import StudentSeatPolicy
from app.services.saas.subscriptions import InstitutionSubscriptionService


class InstitutionPlanOverview:
    """Plano, uso e faturas de uma instituicao (para ela mesma e para o super admin)."""

    def __init__(self, db: Session):
        self.subscriptions = InstitutionSubscriptionService(db)
        self.invoices = PlatformInvoiceService(db)
        self.seats = StudentSeatPolicy(db)

    def for_institution(self, institution_id: UUID) -> InstitutionPlanOut:
        subscription = self.subscriptions.get(institution_id)
        return InstitutionPlanOut(
            subscription=SubscriptionOut.model_validate(subscription) if subscription else None,
            usage=self.seats.usage(institution_id),
            invoices=[PlatformInvoiceOut.model_validate(invoice) for invoice in self.invoices.list(institution_id)],
        )
