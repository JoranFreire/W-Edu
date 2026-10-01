"""Acesso a dados dos planos SaaS (tabelas globais da plataforma)."""

from app.repositories.saas.invoices import PlatformInvoiceRepository
from app.repositories.saas.plans import SaasPlanRepository
from app.repositories.saas.subscriptions import InstitutionSubscriptionRepository

__all__ = ["InstitutionSubscriptionRepository", "PlatformInvoiceRepository", "SaasPlanRepository"]
