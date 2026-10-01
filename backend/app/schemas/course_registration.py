from uuid import UUID
from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.academic import ComponentKind
from app.schemas.academic import SubjectSummary


class RegistrationWindowCreate(BaseModel):
    term_id: UUID
    program_id: UUID | None = None
    name: str = Field(min_length=1, max_length=120)
    opens_at: datetime
    closes_at: datetime
    min_credits: int | None = Field(default=None, ge=0)
    max_credits: int | None = Field(default=None, ge=1)
    allow_waitlist: bool = True


class RegistrationWindowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    min_credits: int | None = Field(default=None, ge=0)
    max_credits: int | None = Field(default=None, ge=1)
    allow_waitlist: bool | None = None


class RegistrationWindowOut(BaseModel):
    id: UUID
    term_id: UUID
    term_name: str
    program_id: UUID | None
    program_name: str | None
    name: str
    opens_at: datetime
    closes_at: datetime
    min_credits: int | None
    max_credits: int | None
    allow_waitlist: bool
    is_open: bool


class TimeSlotCreate(BaseModel):
    weekday: int = Field(ge=0, le=6)
    starts_at: time
    ends_at: time

    @model_validator(mode="after")
    def _ordered(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("O fim deve ser posterior ao início")
        return self


class TimeSlotOut(BaseModel):
    id: UUID
    class_offering_id: UUID
    weekday: int
    starts_at: time
    ends_at: time

    model_config = {"from_attributes": True}


OfferingSituation = Literal["enrolled", "waitlisted", "available", "full", "blocked"]


class CatalogOffering(BaseModel):
    offering_id: UUID
    offering_name: str
    subject: SubjectSummary
    term_number: int | None
    kind: ComponentKind | None
    credits: int
    instructor_name: str | None
    slots: list[TimeSlotOut]
    capacity: int
    seats_taken: int
    situation: OfferingSituation
    waitlist_position: int | None
    blockers: list[str]


class RegistrationCatalogOut(BaseModel):
    window: RegistrationWindowOut | None
    term_id: UUID
    program_enrollment_id: UUID
    registration_number: str
    program_name: str
    credits_registered: int
    min_credits: int | None
    max_credits: int | None
    offerings: list[CatalogOffering]


class MyRegistrationWindowOut(BaseModel):
    window: RegistrationWindowOut
    program_enrollment_id: UUID
    program_name: str


class RegistrationResultOut(BaseModel):
    offering_id: UUID
    result: Literal["enrolled", "waitlisted"]
    waitlist_position: int | None = None


class OfficeRegistrationInput(BaseModel):
    """Inscricao feita pela secretaria; `override` dispensa pre-requisito, choque de horario e vagas."""

    override: bool = False
