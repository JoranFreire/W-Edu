from __future__ import annotations
from uuid import UUID

import calendar
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.saas import PlatformInvoice, PlatformInvoiceStatus, SaasSubscriptionStatus
from app.repositories.saas import PlatformInvoiceRepository
from app.services.academic.errors import conflict, not_found
from app.services.saas.subscriptions import InstitutionSubscriptionService

DAYS_TO_PAY = 10


def month_end(start: date) -> date:
    """Ultimo dia do periodo mensal que comeca em `start` (vespera do mesmo dia no mes seguinte)."""
    year, month = (start.year + 1, 1) if start.month == 12 else (start.year, start.month + 1)
    return date(year, month, min(start.day, calendar.monthrange(year, month)[1])) - timedelta(days=1)


class PlatformInvoiceService:
    """Faturas mensais das instituicoes: geracao por periodo (sem duplicar) e baixa."""

    def __init__(self, db: Session):
        self.repo = PlatformInvoiceRepository(db)
        self.subscriptions = InstitutionSubscriptionService(db)

    def list(self, institution_id: UUID) -> list[PlatformInvoice]:
        return self.repo.list_for(institution_id)

    def generate(self, institution_id: UUID, period_start: date) -> PlatformInvoice:
        subscription = self.subscriptions.get_or_404(institution_id)
        if subscription.status == SaasSubscriptionStatus.cancelled:
            raise conflict("Assinatura cancelada")
        if existing := self.repo.get_period(subscription.id, period_start):
            return existing
        # Periodo de teste nao gera cobranca.
        in_trial = subscription.status == SaasSubscriptionStatus.trial and (subscription.trial_ends_on is None or period_start <= subscription.trial_ends_on)
        return self.repo.save(PlatformInvoice(
            institution_id=institution_id, subscription_id=subscription.id, plan_name=subscription.plan.name,
            period_start=period_start, period_end=month_end(period_start),
            amount_cents=0 if in_trial else subscription.plan.monthly_price_cents,
            due_on=period_start + timedelta(days=DAYS_TO_PAY),
        ))

    def mark_paid(self, invoice_id: UUID) -> PlatformInvoice:
        invoice = self.repo.get_by_id(invoice_id)
        if not invoice:
            raise not_found("Fatura não encontrada")
        if invoice.status != PlatformInvoiceStatus.pending:
            raise conflict("Fatura já quitada ou cancelada")
        invoice.status, invoice.paid_at = PlatformInvoiceStatus.paid, datetime.now(timezone.utc)
        return self.repo.save(invoice)
