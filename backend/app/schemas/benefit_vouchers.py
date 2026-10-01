from uuid import UUID
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.social_programs import BenefitKind
from app.schemas.academic_groups import PersonSummary

VoucherState = Literal["released", "redeemed", "cancelled", "expired"]


class MeetingVoucherInput(BaseModel):
    item_id: UUID
    quantity: int = Field(default=1, ge=1, le=100)
    valid_until: date | None = None


class IndividualVoucherInput(BaseModel):
    item_id: UUID
    student_id: UUID
    class_offering_id: UUID
    quantity: int = Field(default=1, ge=1, le=100)
    valid_until: date | None = None


class MeetingVoucherOut(BaseModel):
    released: int
    available_stock: int


class VoucherOut(BaseModel):
    """Beneficio liberado; `qr_payload` e o conteudo do QR (prefixo + codigo)."""

    id: UUID
    code: str
    qr_payload: str
    status: VoucherState
    item_id: UUID
    item_name: str
    item_kind: BenefitKind
    unit: str
    quantity: int
    student: PersonSummary
    class_offering_id: UUID
    class_offering_name: str
    scheduled_meeting_id: UUID | None
    valid_until: date | None
    released_at: datetime
    redeemed_at: datetime | None


class RedeemInput(BaseModel):
    """Codigo lido do QR (com ou sem o prefixo) ou digitado."""

    code: str = Field(min_length=4, max_length=120)
