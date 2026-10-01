from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.admissions import (
    AdmissionCallStatus, ApplicationStatus, DocumentReview, Schooling, SeatKind, SelectionMethod,
)
from app.schemas.academic_groups import PersonSummary


class AdmissionCallCreate(BaseModel):
    class_offering_id: int
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=8000)
    method: SelectionMethod = SelectionMethod.first_come
    seats: int = Field(ge=1)
    reserved_seats: int = Field(default=0, ge=0)
    reserved_label: str | None = Field(default=None, max_length=200)
    opens_at: datetime
    closes_at: datetime
    confirmation_days: int = Field(default=3, ge=1, le=30)
    min_age: int | None = Field(default=None, ge=0, le=120)
    max_age: int | None = Field(default=None, ge=0, le=120)
    min_schooling: Schooling | None = None
    max_income_per_capita_cents: int | None = Field(default=None, ge=0)
    required_city: str | None = Field(default=None, max_length=120)
    required_documents: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self):
        if self.reserved_seats > self.seats:
            raise ValueError("A reserva não pode passar do total de vagas")
        if self.min_age is not None and self.max_age is not None and self.min_age > self.max_age:
            raise ValueError("Idade mínima maior que a máxima")
        return self


class AdmissionCallUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=8000)
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    confirmation_days: int | None = Field(default=None, ge=1, le=30)


class CallStatusChange(BaseModel):
    status: AdmissionCallStatus


class AdmissionCallOut(BaseModel):
    id: int
    class_offering_id: int
    course_name: str
    offering_name: str
    starts_at: datetime
    title: str
    description: str | None
    method: SelectionMethod
    seats: int
    reserved_seats: int
    reserved_label: str | None
    opens_at: datetime
    closes_at: datetime
    confirmation_days: int
    min_age: int | None
    max_age: int | None
    min_schooling: Schooling | None
    max_income_per_capita_cents: int | None
    required_city: str | None
    required_documents: list[str]
    status: AdmissionCallStatus
    is_accepting: bool
    lottery_seed: str | None
    applications: int


class ApplicationCreate(BaseModel):
    birth_date: date
    schooling: Schooling
    family_income_cents: int = Field(ge=0)
    household_size: int = Field(ge=1, le=30)
    city: str = Field(min_length=1, max_length=120)
    claims_reserved: bool = False


class ApplicationDocumentOut(BaseModel):
    id: int
    kind: str
    file_name: str
    review: DocumentReview
    review_note: str | None

    model_config = {"from_attributes": True}


class ApplicationOut(BaseModel):
    id: int
    call_id: int
    call_title: str
    applicant: PersonSummary
    protocol: str
    birth_date: date
    schooling: Schooling
    family_income_cents: int
    household_size: int
    city: str
    claims_reserved: bool
    reserved_verified: bool | None
    review_score: float | None
    status: ApplicationStatus
    ineligibility_reasons: list[str]
    rank: int | None
    seat_kind: SeatKind | None
    confirm_until: datetime | None
    confirmed_at: datetime | None
    created_at: datetime
    documents: list[ApplicationDocumentOut]


class ApplicationReview(BaseModel):
    """Analise da secretaria: nota, conferencia da reserva e aptidao (com motivo quando inapta)."""

    review_score: float | None = Field(default=None, ge=0, le=1000)
    reserved_verified: bool | None = None
    eligible: bool | None = None
    reason: str | None = Field(default=None, max_length=500)


class DocumentReviewInput(BaseModel):
    review: DocumentReview
    note: str | None = Field(default=None, max_length=1000)


class ResultEntry(BaseModel):
    protocol: str
    rank: int | None
    status: ApplicationStatus
    seat_kind: SeatKind | None


class AdmissionResultOut(BaseModel):
    call_id: int
    title: str
    method: SelectionMethod
    lottery_seed: str | None
    selected_at: datetime | None
    entries: list[ResultEntry]


class SelectionOut(BaseModel):
    ranked: int
    called: int
    waitlisted: int


class DeadlinesOut(BaseModel):
    expired: int
    called: int
    waitlisted: int
