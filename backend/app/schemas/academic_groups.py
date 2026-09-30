from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.academic_groups import ProgramEnrollmentStatus, Shift


class PersonSummary(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ProgramSummary(BaseModel):
    id: int
    code: str
    name: str

    model_config = {"from_attributes": True}


class ProgramEnrollmentCreate(BaseModel):
    student_id: int
    program_id: int
    curriculum_id: int | None = None
    entry_term_id: int | None = None
    registration_number: str | None = Field(default=None, min_length=1, max_length=40)
    enrolled_on: date | None = None


class ProgramEnrollmentStatusChange(BaseModel):
    status: ProgramEnrollmentStatus


class ProgramEnrollmentOut(BaseModel):
    id: int
    registration_number: str
    status: ProgramEnrollmentStatus
    enrolled_on: date
    status_changed_at: datetime
    curriculum_id: int
    entry_term_id: int | None
    concluded_on: date | None = None
    ceremony_on: date | None = None
    student: PersonSummary
    program: ProgramSummary

    model_config = {"from_attributes": True}


class ClassGroupCreate(BaseModel):
    program_id: int
    term_id: int
    name: str = Field(min_length=1, max_length=80)
    curriculum_term_number: int | None = Field(default=None, ge=1)
    shift: Shift = Shift.morning
    capacity: int | None = Field(default=None, ge=1)
    homeroom_teacher_id: int | None = None


class ClassGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    curriculum_term_number: int | None = Field(default=None, ge=1)
    shift: Shift | None = None
    capacity: int | None = Field(default=None, ge=1)
    homeroom_teacher_id: int | None = None


class ClassGroupOut(BaseModel):
    id: int
    program_id: int
    term_id: int
    name: str
    curriculum_term_number: int | None
    shift: Shift
    capacity: int | None
    homeroom_teacher_id: int | None
    member_count: int


class ClassGroupMemberCreate(BaseModel):
    program_enrollment_id: int


class ClassGroupMemberOut(BaseModel):
    id: int
    program_enrollment_id: int
    registration_number: str
    student: PersonSummary
