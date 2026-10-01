from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.saas import PlatformInvoiceStatus, SaasSubscriptionStatus


class SaasPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    monthly_price_cents: int = Field(ge=0)
    max_students: int | None = Field(default=None, ge=1)


class SaasPlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    monthly_price_cents: int | None = Field(default=None, ge=0)
    max_students: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class SaasPlanOut(BaseModel):
    id: int
    name: str
    description: str | None
    monthly_price_cents: int
    max_students: int | None
    is_active: bool

    model_config = {"from_attributes": True}


class SubscriptionInput(BaseModel):
    plan_id: int
    status: SaasSubscriptionStatus = SaasSubscriptionStatus.active
    started_on: date | None = None
    trial_ends_on: date | None = None


class SubscriptionOut(BaseModel):
    institution_id: int
    plan: SaasPlanOut
    status: SaasSubscriptionStatus
    started_on: date
    trial_ends_on: date | None

    model_config = {"from_attributes": True}


class InvoiceGenerate(BaseModel):
    period_start: date


class PlatformInvoiceOut(BaseModel):
    id: int
    institution_id: int
    plan_name: str
    period_start: date
    period_end: date
    amount_cents: int
    due_on: date
    status: PlatformInvoiceStatus
    paid_at: datetime | None

    model_config = {"from_attributes": True}


class UsageOut(BaseModel):
    active_students: int
    max_students: int | None


class InstitutionPlanOut(BaseModel):
    """O que a instituicao contratou, quanto usa e suas faturas."""

    subscription: SubscriptionOut | None
    usage: UsageOut
    invoices: list[PlatformInvoiceOut]
