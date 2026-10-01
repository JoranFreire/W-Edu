from datetime import date

from pydantic import BaseModel, Field

from app.models.social_programs import BenefitKind, FundingKind, StockOrigin
from app.schemas.academic_groups import PersonSummary


class FundingSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: FundingKind = FundingKind.agreement
    agreement_number: str | None = Field(default=None, max_length=80)
    amount_cents: int | None = Field(default=None, ge=0)
    starts_on: date
    ends_on: date | None = None
    notes: str | None = Field(default=None, max_length=4000)


class FundingSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    agreement_number: str | None = Field(default=None, max_length=80)
    amount_cents: int | None = Field(default=None, ge=0)
    ends_on: date | None = None
    notes: str | None = Field(default=None, max_length=4000)
    is_active: bool | None = None


class FundingSourceOut(BaseModel):
    id: int
    name: str
    kind: FundingKind
    agreement_number: str | None
    amount_cents: int | None
    starts_on: date
    ends_on: date | None
    notes: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class BenefitItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: BenefitKind = BenefitKind.other
    unit: str = Field(default="unidade", min_length=1, max_length=40)
    unit_cost_cents: int = Field(default=0, ge=0)
    requires_attendance: bool = False


class BenefitItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    requires_attendance: bool | None = None
    is_active: bool | None = None


class BenefitItemOut(BaseModel):
    id: int
    name: str
    kind: BenefitKind
    unit: str
    unit_cost_cents: int
    requires_attendance: bool
    is_active: bool
    stock: int


class StockEntryCreate(BaseModel):
    quantity: int = Field(ge=1)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    origin: StockOrigin = StockOrigin.purchase
    funding_source_id: int | None = None
    received_on: date
    notes: str | None = Field(default=None, max_length=2000)


class StockEntryOut(BaseModel):
    id: int
    item_id: int
    quantity: int
    unit_cost_cents: int
    origin: StockOrigin
    funding_source_id: int | None
    received_on: date

    model_config = {"from_attributes": True}


class MeetingDeliveryInput(BaseModel):
    item_id: int
    quantity: int = Field(default=1, ge=1, le=100)


class IndividualDeliveryInput(BaseModel):
    item_id: int
    student_id: int
    class_offering_id: int
    quantity: int = Field(default=1, ge=1, le=100)
    delivered_on: date | None = None


class DeliveryOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    student: PersonSummary
    class_offering_id: int
    scheduled_meeting_id: int | None
    quantity: int
    unit_cost_cents: int
    delivered_on: date


class MeetingDeliveryOut(BaseModel):
    delivered: int
    remaining_stock: int


class OfferingIndicators(BaseModel):
    class_offering_id: int | None
    name: str
    applications: int
    enrolled: int
    active: int
    completed: int
    dismissed: int
    dropped: int
    evasion_rate: float


class BenefitUsage(BaseModel):
    item_name: str
    unit: str
    quantity: int
    cost_cents: int


class ProfileOut(BaseModel):
    """Perfil de quem foi matriculado pelo processo seletivo (questionario socioeconomico)."""

    respondents: int
    age: dict[str, int]
    income_per_capita: dict[str, int]
    schooling: dict[str, int]
    reserved_seats: int


class FundingReportOut(BaseModel):
    funding: FundingSourceOut
    offerings: list[OfferingIndicators]
    totals: OfferingIndicators
    profile: ProfileOut
    benefits: list[BenefitUsage]
    stock_received_cents: int
    benefits_cost_cents: int
    budget_balance_cents: int | None
    minimum_wage_cents: int
    minimum_wage_source: str
