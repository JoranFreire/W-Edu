from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.completion import ActivityCategory, FinalProjectStatus, InternshipStatus, ReviewStatus
from app.schemas.academic_groups import PersonSummary


class ActivityCreate(BaseModel):
    category: ActivityCategory = ActivityCategory.other
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    occurred_on: date
    hours_requested: int = Field(ge=1, le=1000)


class ActivityDecision(BaseModel):
    approved: bool
    hours_approved: int | None = Field(default=None, ge=1, le=1000)
    note: str | None = Field(default=None, max_length=2000)


class ActivityOut(BaseModel):
    id: int
    program_enrollment_id: int
    category: ActivityCategory
    title: str
    description: str | None
    occurred_on: date
    hours_requested: int
    hours_approved: int | None
    status: ReviewStatus
    decision_note: str | None
    decided_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InternshipCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    supervisor_name: str | None = Field(default=None, max_length=200)
    advisor_id: int | None = None
    is_mandatory: bool = True
    agreement_number: str | None = Field(default=None, max_length=80)
    starts_on: date
    ends_on: date | None = None
    planned_hours: int | None = Field(default=None, ge=1)
    notes: str | None = Field(default=None, max_length=4000)


class InternshipUpdate(BaseModel):
    supervisor_name: str | None = Field(default=None, max_length=200)
    advisor_id: int | None = None
    agreement_number: str | None = Field(default=None, max_length=80)
    ends_on: date | None = None
    planned_hours: int | None = Field(default=None, ge=1)
    status: InternshipStatus | None = None
    notes: str | None = Field(default=None, max_length=4000)


class InternshipOut(BaseModel):
    id: int
    program_enrollment_id: int
    student: PersonSummary
    company_name: str
    supervisor_name: str | None
    advisor: PersonSummary | None
    is_mandatory: bool
    agreement_number: str | None
    starts_on: date
    ends_on: date | None
    planned_hours: int | None
    status: InternshipStatus
    notes: str | None
    approved_hours: int
    pending_hours: int


class InternshipLogCreate(BaseModel):
    worked_on: date
    hours: int = Field(ge=1, le=12)
    activities: str = Field(min_length=1, max_length=4000)


class LogReview(BaseModel):
    approved: bool


class InternshipLogOut(BaseModel):
    id: int
    internship_id: int
    worked_on: date
    hours: int
    activities: str
    status: ReviewStatus
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}


class FinalProjectInput(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    advisor_id: int | None = None
    co_advisor_name: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)


class FinalProjectResult(BaseModel):
    """Entrega (`submitted`) ou resultado da defesa (`approved`/`failed`, com data e nota)."""

    status: Literal["submitted", "approved", "failed"]
    defense_on: date | None = None
    grade: float | None = Field(default=None, ge=0)
    committee: str | None = Field(default=None, max_length=2000)


class FinalProjectOut(BaseModel):
    id: int
    program_enrollment_id: int
    student: PersonSummary
    title: str
    advisor: PersonSummary | None
    co_advisor_name: str | None
    status: FinalProjectStatus
    defense_on: date | None
    grade: float | None
    committee: str | None
    notes: str | None


RequirementKey = Literal["mandatory_hours", "total_hours", "credits", "complementary_hours", "internship_hours", "final_project"]


class RequirementOut(BaseModel):
    key: RequirementKey
    label: str
    done: int
    required: int
    unit: str
    met: bool


class IntegralizationOut(BaseModel):
    program_enrollment_id: int
    registration_number: str
    program_name: str
    cr: float | None
    requirements: list[RequirementOut]
    complete: bool


class AdvisingOut(BaseModel):
    """O que o docente orienta: estagios (com horas a validar) e TCCs."""

    internships: list[InternshipOut]
    final_projects: list[FinalProjectOut]
