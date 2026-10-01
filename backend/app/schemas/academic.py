from uuid import UUID
from datetime import date

from pydantic import BaseModel, Field

from app.models.academic import AcademicUnitKind, ComponentKind, CurriculumStatus, ProgramLevel, ProgramStatus


CODE = Field(min_length=1, max_length=40)


class AcademicUnitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: AcademicUnitKind = AcademicUnitKind.other
    parent_id: UUID | None = None
    is_active: bool = True


class AcademicUnitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    kind: AcademicUnitKind | None = None
    parent_id: UUID | None = None
    is_active: bool | None = None


class AcademicUnitOut(BaseModel):
    id: UUID
    name: str
    kind: AcademicUnitKind
    parent_id: UUID | None
    is_active: bool

    model_config = {"from_attributes": True}


class ProgramCreate(BaseModel):
    code: str = CODE
    name: str = Field(min_length=1, max_length=200)
    level: ProgramLevel = ProgramLevel.free
    unit_id: UUID | None = None
    degree: str | None = None
    duration_terms: int | None = Field(default=None, ge=1)
    total_hours: int | None = Field(default=None, ge=0)
    total_credits: int | None = Field(default=None, ge=0)
    complementary_hours: int | None = Field(default=None, ge=0)
    internship_hours: int | None = Field(default=None, ge=0)
    requires_final_project: bool = False
    status: ProgramStatus = ProgramStatus.draft


class ProgramUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    level: ProgramLevel | None = None
    unit_id: UUID | None = None
    degree: str | None = None
    duration_terms: int | None = Field(default=None, ge=1)
    total_hours: int | None = Field(default=None, ge=0)
    total_credits: int | None = Field(default=None, ge=0)
    complementary_hours: int | None = Field(default=None, ge=0)
    internship_hours: int | None = Field(default=None, ge=0)
    requires_final_project: bool | None = None
    status: ProgramStatus | None = None


class ProgramOut(BaseModel):
    id: UUID
    code: str
    name: str
    level: ProgramLevel
    unit_id: UUID | None
    degree: str | None
    duration_terms: int | None
    total_hours: int | None
    total_credits: int | None
    complementary_hours: int | None
    internship_hours: int | None
    requires_final_project: bool
    status: ProgramStatus

    model_config = {"from_attributes": True}


class SubjectCreate(BaseModel):
    code: str = CODE
    name: str = Field(min_length=1, max_length=200)
    syllabus: str | None = None
    hours: int = Field(default=0, ge=0)
    credits: int | None = Field(default=None, ge=0)
    course_id: UUID | None = None
    is_active: bool = True


class SubjectUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    syllabus: str | None = None
    hours: int | None = Field(default=None, ge=0)
    credits: int | None = Field(default=None, ge=0)
    course_id: UUID | None = None
    is_active: bool | None = None


class SubjectOut(BaseModel):
    id: UUID
    code: str
    name: str
    syllabus: str | None
    hours: int
    credits: int | None
    course_id: UUID | None
    is_active: bool

    model_config = {"from_attributes": True}


class SubjectSummary(BaseModel):
    id: UUID
    code: str
    name: str

    model_config = {"from_attributes": True}


class SubjectLinkCreate(BaseModel):
    subject_id: UUID


class CurriculumCreate(BaseModel):
    version: str = Field(min_length=1, max_length=40)
    valid_from: date | None = None
    notes: str | None = None


class CurriculumUpdate(BaseModel):
    version: str | None = Field(default=None, min_length=1, max_length=40)
    valid_from: date | None = None
    notes: str | None = None


class CurriculumNewVersion(BaseModel):
    version: str = Field(min_length=1, max_length=40)
    valid_from: date | None = None


class CurriculumOut(BaseModel):
    id: UUID
    program_id: UUID
    version: str
    valid_from: date | None
    status: CurriculumStatus
    notes: str | None

    model_config = {"from_attributes": True}


class CurriculumComponentCreate(BaseModel):
    subject_id: UUID
    term_number: int = Field(ge=1)
    kind: ComponentKind = ComponentKind.mandatory
    hours: int | None = Field(default=None, ge=0)
    credits: int | None = Field(default=None, ge=0)


class CurriculumComponentUpdate(BaseModel):
    term_number: int | None = Field(default=None, ge=1)
    kind: ComponentKind | None = None
    hours: int | None = Field(default=None, ge=0)
    credits: int | None = Field(default=None, ge=0)


class CurriculumComponentOut(BaseModel):
    id: UUID
    subject: SubjectSummary
    term_number: int
    kind: ComponentKind
    hours: int
    credits: int | None
    # Valores definidos na propria matriz (vazio = usa os da disciplina).
    hours_override: int | None
    credits_override: int | None


class CurriculumTotals(BaseModel):
    hours: int
    credits: int
    mandatory_hours: int
    terms: int


class CurriculumDetail(CurriculumOut):
    components: list[CurriculumComponentOut]
    totals: CurriculumTotals
    issues: list[str]
