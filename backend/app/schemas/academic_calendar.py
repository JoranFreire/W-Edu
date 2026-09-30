from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.models.academic_calendar import CalendarEventKind, GradingPeriodStatus, TermKind, TermStatus


class _DateRange(BaseModel):
    @model_validator(mode="after")
    def _check_range(self):
        starts_on, ends_on = getattr(self, "starts_on", None), getattr(self, "ends_on", None)
        if starts_on and ends_on and ends_on < starts_on:
            raise ValueError("A data final não pode ser anterior à inicial")
        return self


class AcademicTermCreate(_DateRange):
    name: str = Field(min_length=1, max_length=80)
    kind: TermKind = TermKind.semester
    starts_on: date
    ends_on: date


class AcademicTermUpdate(_DateRange):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    kind: TermKind | None = None
    starts_on: date | None = None
    ends_on: date | None = None


class TermStatusChange(BaseModel):
    status: TermStatus


class AcademicTermOut(BaseModel):
    id: int
    name: str
    kind: TermKind
    starts_on: date
    ends_on: date
    status: TermStatus

    model_config = {"from_attributes": True}


class GradingPeriodCreate(_DateRange):
    name: str = Field(min_length=1, max_length=80)
    order: int | None = Field(default=None, ge=1)
    starts_on: date
    ends_on: date
    weight: float = Field(default=1, ge=0)


class GradingPeriodUpdate(_DateRange):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    starts_on: date | None = None
    ends_on: date | None = None
    weight: float | None = Field(default=None, ge=0)


class GradingPeriodStatusChange(BaseModel):
    status: GradingPeriodStatus


class GradingPeriodOut(BaseModel):
    id: int
    term_id: int
    name: str
    order: int
    starts_on: date
    ends_on: date
    weight: float
    status: GradingPeriodStatus

    model_config = {"from_attributes": True}


class CalendarEventCreate(_DateRange):
    kind: CalendarEventKind
    title: str = Field(min_length=1, max_length=200)
    starts_on: date
    ends_on: date | None = None
    term_id: int | None = None


class CalendarEventUpdate(_DateRange):
    kind: CalendarEventKind | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    starts_on: date | None = None
    ends_on: date | None = None


class CalendarEventOut(BaseModel):
    id: int
    term_id: int | None
    kind: CalendarEventKind
    title: str
    starts_on: date
    ends_on: date | None

    model_config = {"from_attributes": True}


class TermCalendarSummary(BaseModel):
    school_days: int
    non_school_days: int
    extra_school_days: int
    exams: int
