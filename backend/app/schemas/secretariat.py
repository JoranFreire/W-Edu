from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.academic import ComponentKind
from app.models.secretariat import CreditTransferOrigin, CreditTransferStatus, DeclarationKind, EnrollmentEventKind


class ReasonInput(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class TransferOutInput(ReasonInput):
    destination: str = Field(min_length=1, max_length=200)


class InternalTransferInput(ReasonInput):
    program_id: int
    curriculum_id: int | None = None


class CurriculumChangeInput(ReasonInput):
    curriculum_id: int


class ReenrollInput(BaseModel):
    term_id: int
    curriculum_term_number: int | None = Field(default=None, ge=1)


class EnrollmentEventOut(BaseModel):
    id: int
    kind: EnrollmentEventKind
    term_id: int | None
    reason: str | None
    details: dict
    created_by_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TermRegistrationOut(BaseModel):
    id: int
    term_id: int
    term_name: str
    curriculum_term_number: int | None
    registered_at: datetime


class CreditTransferCreate(BaseModel):
    subject_id: int
    origin: CreditTransferOrigin = CreditTransferOrigin.external
    source_institution: str | None = Field(default=None, max_length=200)
    source_subject: str = Field(min_length=1, max_length=200)
    grade: float | None = Field(default=None, ge=0)
    hours: int | None = Field(default=None, ge=0)


class CreditTransferDecision(BaseModel):
    approved: bool
    note: str | None = Field(default=None, max_length=1000)


class CreditTransferOut(BaseModel):
    id: int
    subject_id: int
    subject_code: str
    subject_name: str
    origin: CreditTransferOrigin
    source_institution: str | None
    source_subject: str
    grade: float | None
    hours: int | None
    status: CreditTransferStatus
    decision_note: str | None
    decided_at: datetime | None
    created_at: datetime


class TranscriptRow(BaseModel):
    subject_id: int
    code: str
    name: str
    term_number: int
    kind: ComponentKind
    hours: int
    credits: int | None
    status: str          # completed | credited | in_progress | failed | pending
    grade: float | None
    taken_in: str | None  # periodo letivo (ou instituicao de origem no aproveitamento)
    attempts: int


class TranscriptSummary(BaseModel):
    cr: float | None
    mandatory_hours: int
    mandatory_hours_done: int
    elective_hours_done: int
    hours_done: int
    integralization: float
    completed_components: int
    total_components: int


class TranscriptOut(BaseModel):
    program_enrollment_id: int
    registration_number: str
    student_name: str
    program_code: str
    program_name: str
    curriculum_version: str
    status: str
    rows: list[TranscriptRow]
    summary: TranscriptSummary


class DeclarationCreate(BaseModel):
    kind: DeclarationKind
    term_id: int | None = None


class DeclarationRevoke(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class DeclarationOut(BaseModel):
    id: int
    program_enrollment_id: int
    kind: DeclarationKind
    term_id: int | None
    title: str
    lines: list[str]
    validation_code: str
    issued_at: datetime
    revoked_at: datetime | None
    revoked_reason: str | None

    model_config = {"from_attributes": True}


class DeclarationValidationOut(BaseModel):
    valid: bool
    message: str
    kind: DeclarationKind | None = None
    title: str | None = None
    student_name: str | None = None
    institution_name: str | None = None
    issued_at: datetime | None = None


class ConclusionCheckOut(BaseModel):
    eligible: bool
    status: str
    integralization: float
    hours_done: int
    required_hours: int | None
    missing: list[str]


class ConclusionInput(BaseModel):
    concluded_on: date
    ceremony_on: date | None = None


class CeremonyInput(BaseModel):
    ceremony_on: date
