from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.assessment import AssessmentKind, AverageFormula, GradingScale
from app.schemas.academic_groups import PersonSummary


class ConceptBand(BaseModel):
    code: str = Field(min_length=1, max_length=10)
    min_value: float


class _SchemeRules(BaseModel):
    @model_validator(mode="after")
    def _check_bounds(self):
        low, high, passing = getattr(self, "min_value", None), getattr(self, "max_value", None), getattr(self, "passing_grade", None)
        if low is not None and high is not None and high <= low:
            raise ValueError("Nota máxima deve ser maior que a mínima")
        if passing is not None and high is not None and low is not None and not low <= passing <= high:
            raise ValueError("Média de aprovação fora da escala")
        return self


class GradingSchemeCreate(_SchemeRules):
    name: str = Field(min_length=1, max_length=120)
    scale: GradingScale = GradingScale.numeric
    min_value: float = 0
    max_value: float = 10
    passing_grade: float = 6
    formula: AverageFormula = AverageFormula.weighted
    recovery_enabled: bool = True
    min_attendance: float = Field(default=75, ge=0, le=100)
    concepts: list[ConceptBand] = Field(default_factory=list)
    is_default: bool = False


class GradingSchemeUpdate(_SchemeRules):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    scale: GradingScale | None = None
    min_value: float | None = None
    max_value: float | None = None
    passing_grade: float | None = None
    formula: AverageFormula | None = None
    recovery_enabled: bool | None = None
    min_attendance: float | None = Field(default=None, ge=0, le=100)
    concepts: list[ConceptBand] | None = None
    is_default: bool | None = None


class GradingSchemeOut(BaseModel):
    id: int | None
    name: str
    scale: GradingScale
    min_value: float
    max_value: float
    passing_grade: float
    formula: AverageFormula
    recovery_enabled: bool
    min_attendance: float
    concepts: list[ConceptBand]
    is_default: bool

    model_config = {"from_attributes": True}


class TeachingOfferingOut(BaseModel):
    id: int
    name: str
    course_id: int
    instructor_id: int | None
    term_id: int | None
    subject_id: int | None
    class_group_id: int | None
    grading_scheme_id: int | None
    starts_at: datetime
    ends_at: datetime

    model_config = {"from_attributes": True}


class AssessmentItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    kind: AssessmentKind = AssessmentKind.test
    grading_period_id: int | None = None
    weight: float = Field(default=1, ge=0)
    max_score: float = Field(default=10, gt=0)
    quiz_id: int | None = None
    due_on: date | None = None


class AssessmentItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    kind: AssessmentKind | None = None
    weight: float | None = Field(default=None, ge=0)
    max_score: float | None = Field(default=None, gt=0)
    quiz_id: int | None = None
    due_on: date | None = None


class AssessmentItemOut(BaseModel):
    id: int
    class_offering_id: int
    grading_period_id: int | None
    name: str
    kind: AssessmentKind
    weight: float
    max_score: float
    quiz_id: int | None
    due_on: date | None

    model_config = {"from_attributes": True}


class GradeInput(BaseModel):
    class_enrollment_id: int
    score: float | None = Field(default=None, ge=0)
    notes: str | None = None


class GradeRow(BaseModel):
    class_enrollment_id: int
    student: PersonSummary
    score: float | None
    notes: str | None


class QuizImportResult(BaseModel):
    imported: int
    without_attempt: int


class GradebookPeriod(BaseModel):
    id: int | None
    name: str
    status: str


class GradebookRow(BaseModel):
    class_enrollment_id: int
    student: PersonSummary
    scores: dict[str, float | None]
    period_averages: dict[str, float | None]
    average: float | None
    concept: str | None
    absences: int
    attendance_rate: float | None


class GradebookOut(BaseModel):
    scheme: GradingSchemeOut
    periods: list[GradebookPeriod]
    items: list[AssessmentItemOut]
    rows: list[GradebookRow]
    total_lessons: int


class DiaryEntryCreate(BaseModel):
    date: date
    lesson_count: int = Field(default=1, ge=1, le=12)
    content_taught: str = Field(min_length=1)
    scheduled_meeting_id: int | None = None


class DiaryEntryUpdate(BaseModel):
    lesson_count: int | None = Field(default=None, ge=1, le=12)
    content_taught: str | None = Field(default=None, min_length=1)


class DiaryEntryOut(BaseModel):
    id: int
    class_offering_id: int
    date: date
    lesson_count: int
    content_taught: str
    instructor_id: int | None
    scheduled_meeting_id: int | None
    locked: bool = False


class DiaryAttendanceInput(BaseModel):
    class_enrollment_id: int
    absences: int = Field(ge=0)
    justified: bool = False
    note: str | None = Field(default=None, max_length=300)


class DiaryAttendanceRow(BaseModel):
    class_enrollment_id: int
    student: PersonSummary
    absences: int
    justified: bool
    note: str | None


class SyncEnrollmentsResult(BaseModel):
    created: int
