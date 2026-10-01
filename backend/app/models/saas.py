"""Planos SaaS da plataforma: o super admin cobra cada instituicao pelo plano contratado (tabelas globais, sem tenant)."""

from uuid import UUID

from app.core.ids import new_id
from datetime import date, datetime, timezone
import enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SaasSubscriptionStatus(str, enum.Enum):
    trial = "trial"
    active = "active"
    past_due = "past_due"
    cancelled = "cancelled"


class PlatformInvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class SaasPlan(Base):
    __tablename__ = "saas_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    monthly_price_cents: Mapped[int] = mapped_column(Integer)
    # Vazio: sem limite de alunos ativos.
    max_students: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class InstitutionSubscription(Base):
    """Plano contratado pela instituicao (uma assinatura por instituicao)."""

    __tablename__ = "institution_subscriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    institution_id: Mapped[UUID] = mapped_column(ForeignKey("institutions.id"), unique=True, index=True)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("saas_plans.id"), index=True)
    status: Mapped[SaasSubscriptionStatus] = mapped_column(SAEnum(SaasSubscriptionStatus), default=SaasSubscriptionStatus.trial)
    started_on: Mapped[date] = mapped_column(Date)
    trial_ends_on: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    plan: Mapped["SaasPlan"] = relationship()


class PlatformInvoice(Base):
    """Fatura mensal da instituicao (uma por assinatura e inicio de periodo)."""

    __tablename__ = "platform_invoices"
    __table_args__ = (UniqueConstraint("subscription_id", "period_start"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    institution_id: Mapped[UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    subscription_id: Mapped[UUID] = mapped_column(ForeignKey("institution_subscriptions.id"), index=True)
    plan_name: Mapped[str] = mapped_column(String(120))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    amount_cents: Mapped[int] = mapped_column(Integer)
    due_on: Mapped[date] = mapped_column(Date)
    status: Mapped[PlatformInvoiceStatus] = mapped_column(SAEnum(PlatformInvoiceStatus), default=PlatformInvoiceStatus.pending)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
