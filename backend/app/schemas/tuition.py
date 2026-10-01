from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.finance import ChargeStatus, PaymentMethod
from app.models.tuition import DiscountKind, TuitionBasis
from app.schemas.academic_groups import PersonSummary


class TuitionPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    basis: TuitionBasis = TuitionBasis.program
    term_id: int
    program_id: int | None = None
    class_group_id: int | None = None
    amount_cents: int = Field(ge=1)
    installments: int = Field(default=1, ge=1, le=24)
    first_due_on: date


class TuitionPlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    amount_cents: int | None = Field(default=None, ge=1)
    installments: int | None = Field(default=None, ge=1, le=24)
    first_due_on: date | None = None
    is_active: bool | None = None


class TuitionPlanOut(BaseModel):
    id: int
    name: str
    basis: TuitionBasis
    term_id: int
    term_name: str
    program_id: int | None
    program_name: str | None
    class_group_id: int | None
    class_group_name: str | None
    amount_cents: int
    installments: int
    first_due_on: date
    is_active: bool


class GenerationOut(BaseModel):
    enrollments: int
    created: int
    skipped: int


class DiscountCreate(BaseModel):
    kind: DiscountKind = DiscountKind.other
    percent: float | None = Field(default=None, gt=0, le=100)
    amount_cents: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, max_length=2000)
    valid_from: date
    valid_until: date | None = None

    @model_validator(mode="after")
    def _one_value(self):
        if (self.percent is None) == (self.amount_cents is None):
            raise ValueError("Informe percentual ou valor fixo")
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("O fim da vigência não pode ser anterior ao início")
        return self


class DiscountOut(BaseModel):
    id: int
    program_enrollment_id: int
    kind: DiscountKind
    percent: float | None
    amount_cents: int | None
    description: str | None
    valid_from: date
    valid_until: date | None
    is_active: bool

    model_config = {"from_attributes": True}


class LateFeeSettings(BaseModel):
    fine_percent: float = Field(default=2.0, ge=0, le=20)
    monthly_interest_percent: float = Field(default=1.0, ge=0, le=10)


class SettlementOut(BaseModel):
    on: date
    base_cents: int
    punctuality_discount_cents: int
    fine_cents: int
    interest_cents: int
    total_cents: int


class SettleInput(BaseModel):
    paid_on: date | None = None
    payment_method: PaymentMethod = PaymentMethod.manual


class TuitionChargeOut(BaseModel):
    id: int
    student: PersonSummary | None
    payer: PersonSummary | None
    program_enrollment_id: int | None
    tuition_plan_id: int | None
    installment_number: int | None
    description: str | None
    due_on: date | None
    status: ChargeStatus
    gross_amount_cents: int | None
    discount_cents: int
    punctuality_discount_cents: int
    amount_cents: int
    fine_cents: int
    interest_cents: int
    amount_paid_cents: int | None
    paid_at: datetime | None
    quote: SettlementOut | None
