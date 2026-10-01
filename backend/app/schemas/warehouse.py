from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.warehouse import EntryOrigin, MaterialKind, RequestStatus
from app.schemas.academic_groups import PersonSummary


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=80)
    kind: MaterialKind = MaterialKind.consumable
    unit: str = Field(default="unidade", min_length=1, max_length=40)
    min_stock: int = Field(default=0, ge=0)
    location: str | None = Field(default=None, max_length=120)
    unit_cost_cents: int = Field(default=0, ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=80)
    min_stock: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=120)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ItemOut(BaseModel):
    id: UUID
    name: str
    category: str | None
    kind: MaterialKind
    unit: str
    min_stock: int
    location: str | None
    unit_cost_cents: int
    is_active: bool
    available: int      # no almoxarifado agora
    on_loan: int        # permanentes emprestados
    below_minimum: bool


class EntryCreate(BaseModel):
    quantity: int = Field(ge=1)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    origin: EntryOrigin = EntryOrigin.purchase
    funding_source_id: UUID | None = None
    received_on: date
    notes: str | None = Field(default=None, max_length=2000)


class EntryOut(BaseModel):
    id: UUID
    item_id: UUID
    quantity: int
    unit_cost_cents: int
    origin: EntryOrigin
    funding_source_id: UUID | None
    received_on: date

    model_config = {"from_attributes": True}


class RequestLineInput(BaseModel):
    item_id: UUID
    quantity: int = Field(ge=1, le=10000)


class RequestCreate(BaseModel):
    purpose: str = Field(min_length=1, max_length=2000)
    needed_on: date
    class_offering_id: UUID | None = None
    lines: list[RequestLineInput] = Field(min_length=1)


class LineApproval(BaseModel):
    line_id: UUID
    quantity: int = Field(ge=0)


class ApprovalInput(BaseModel):
    """Quantidade aprovada por linha (zero recusa a linha); tudo zero recusa a requisicao."""

    lines: list[LineApproval]
    return_due_on: date | None = None
    note: str | None = Field(default=None, max_length=2000)


class RejectInput(BaseModel):
    note: str = Field(min_length=1, max_length=2000)


class LineReturn(BaseModel):
    line_id: UUID
    returned: int = Field(default=0, ge=0)
    lost: int = Field(default=0, ge=0)


class ReturnInput(BaseModel):
    lines: list[LineReturn] = Field(min_length=1)


class RequestLineOut(BaseModel):
    id: UUID
    item_id: UUID
    item_name: str
    kind: MaterialKind
    unit: str
    quantity_requested: int
    quantity_approved: int | None
    quantity_delivered: int
    quantity_returned: int
    quantity_lost: int
    outstanding: int


class RequestOut(BaseModel):
    id: UUID
    requester: PersonSummary
    class_offering_id: UUID | None
    class_offering_name: str | None
    purpose: str
    needed_on: date
    status: RequestStatus
    decision_note: str | None
    decided_at: datetime | None
    delivered_at: datetime | None
    return_due_on: date | None
    overdue: bool
    created_at: datetime
    lines: list[RequestLineOut]


class ConsumptionRow(BaseModel):
    label: str
    quantity: int
    cost_cents: int


class ConsumptionOut(BaseModel):
    by_item: list[ConsumptionRow]
    by_requester: list[ConsumptionRow]
    by_offering: list[ConsumptionRow]
    total_cost_cents: int
