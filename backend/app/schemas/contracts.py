from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.contracts import ContractKind, ContractStatus


class ContractTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: ContractKind = ContractKind.enrollment
    body: str = Field(min_length=1, max_length=50000)


class ContractTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=50000)
    is_active: bool | None = None


class ContractTemplateOut(BaseModel):
    id: UUID
    name: str
    kind: ContractKind
    body: str
    is_active: bool

    model_config = {"from_attributes": True}


class ContractIssue(BaseModel):
    template_id: UUID
    term_id: UUID | None = None


class ContractOut(BaseModel):
    id: UUID
    program_enrollment_id: UUID
    student_name: str
    registration_number: str
    kind: ContractKind
    title: str
    body: str
    status: ContractStatus
    validation_code: str
    signer_name: str | None
    signed_at: datetime | None
    document_id: UUID | None
    created_at: datetime


class ContractValidationOut(BaseModel):
    valid: bool
    message: str
    title: str | None = None
    student_name: str | None = None
    institution_name: str | None = None
    signer_name: str | None = None
    signed_at: datetime | None = None
