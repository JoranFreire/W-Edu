from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.academic import ProgramLevel
from app.models.course import CourseModality
from app.models.institution import InstitutionType
from app.models.sales import LeadStatus
from app.schemas.admissions import AdmissionCallOut
from app.schemas.institution import InstitutionSummary
from app.schemas.public_profile import PublicProfile


class PublicProgram(BaseModel):
    id: UUID
    code: str
    name: str
    level: ProgramLevel
    degree: str | None = None
    duration_terms: int | None = None
    total_hours: int | None = None


class PublicCourse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    modality: CourseModality


class PublicCampus(BaseModel):
    name: str
    address: str | None = None


class InstitutionPageOut(BaseModel):
    institution: InstitutionSummary
    profile: PublicProfile
    programs: list[PublicProgram]
    courses: list[PublicCourse]
    campuses: list[PublicCampus]
    open_calls: list[AdmissionCallOut]


class PublicPlanOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    monthly_price_cents: int
    max_students: int | None = None

    model_config = {"from_attributes": True}


class SalesLeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    institution_name: str = Field(min_length=2, max_length=200)
    institution_type: InstitutionType
    students_estimate: int | None = Field(default=None, ge=0, le=1_000_000)
    plan_id: UUID | None = None
    message: str | None = Field(default=None, max_length=4000)
    # Campo-armadilha: invisivel para pessoas; robos que o preenchem sao descartados.
    website: str | None = None

    @field_validator("name", "institution_name")
    @classmethod
    def strip(cls, value: str) -> str:
        return value.strip()


class SalesLeadUpdate(BaseModel):
    status: LeadStatus | None = None
    notes: str | None = Field(default=None, max_length=4000)


class SalesLeadOut(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str | None
    institution_name: str
    institution_type: InstitutionType
    students_estimate: int | None
    plan_id: UUID | None
    plan_name: str | None = None
    message: str | None
    status: LeadStatus
    notes: str | None
    created_at: datetime


class CustomDomainInput(BaseModel):
    custom_domain: str | None = Field(default=None, max_length=253)
