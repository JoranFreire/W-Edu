from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.assessment import AssessmentKind, AverageFormula, GradingScale
from app.models.schedule import ClassEnrollmentResult
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
    id: UUID | None
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
    id: UUID
    name: str
    course_id: UUID
    instructor_id: UUID | None
    term_id: UUID | None
    subject_id: UUID | None
    class_group_id: UUID | None
    grading_scheme_id: UUID | None
    starts_at: datetime
    ends_at: datetime

    model_config = {"from_attributes": True}


class AssessmentItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    kind: AssessmentKind = AssessmentKind.test
    grading_period_id: UUID | None = None
    weight: float = Field(default=1, ge=0)
    max_score: float = Field(default=10, gt=0)
    quiz_id: UUID | None = None
    due_on: date | None = None


class AssessmentItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    kind: AssessmentKind | None = None
    weight: float | None = Field(default=None, ge=0)
    max_score: float | None = Field(default=None, gt=0)
    quiz_id: UUID | None = None
    due_on: date | None = None


class AssessmentItemOut(BaseModel):
    id: UUID
    class_offering_id: UUID
    grading_period_id: UUID | None
    name: str
    kind: AssessmentKind
    weight: float
    max_score: float
    quiz_id: UUID | None
    due_on: date | None

    model_config = {"from_attributes": True}


class GradeInput(BaseModel):
    class_enrollment_id: UUID
    score: float | None = Field(default=None, ge=0)
    notes: str | None = None


class GradeRow(BaseModel):
    class_enrollment_id: UUID
    student: PersonSummary
    score: float | None
    notes: str | None


class QuizImportResult(BaseModel):
    imported: int
    without_attempt: int


class GradebookPeriod(BaseModel):
    id: UUID | None
    name: str
    status: str


class GradebookRow(BaseModel):
    class_enrollment_id: UUID
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
    scheduled_meeting_id: UUID | None = None


class DiaryEntryUpdate(BaseModel):
    lesson_count: int | None = Field(default=None, ge=1, le=12)
    content_taught: str | None = Field(default=None, min_length=1)


class DiaryEntryOut(BaseModel):
    id: UUID
    class_offering_id: UUID
    date: date
    lesson_count: int
    content_taught: str
    instructor_id: UUID | None
    scheduled_meeting_id: UUID | None
    locked: bool = False


class DiaryAttendanceInput(BaseModel):
    class_enrollment_id: UUID
    absences: int = Field(ge=0)
    justified: bool = False
    note: str | None = Field(default=None, max_length=300)


class DiaryAttendanceRow(BaseModel):
    class_enrollment_id: UUID
    student: PersonSummary
    absences: int
    justified: bool
    note: str | None


class SyncEnrollmentsResult(BaseModel):
    created: int


class PeriodClosureOut(BaseModel):
    grading_period_id: UUID
    closed_students: int


class PeriodResultOut(BaseModel):
    grading_period_id: UUID
    average: float | None
    absences: int


class FinalResultRow(BaseModel):
    class_enrollment_id: UUID
    student: PersonSummary
    periods: list[PeriodResultOut]
    average: float | None
    recovery_score: float | None
    final_grade: float | None
    attendance_rate: float | None
    result: ClassEnrollmentResult


class OfferingResultsOut(BaseModel):
    scheme: GradingSchemeOut
    closed_period_ids: list[UUID]
    pending_period_ids: list[UUID]
    finalized: bool
    rows: list[FinalResultRow]


class RecoveryInput(BaseModel):
    class_enrollment_id: UUID
    score: float | None = Field(default=None, ge=0)


class ReportCardPeriod(BaseModel):
    name: str
    average: float | None
    absences: int


class ReportCardEntry(BaseModel):
    class_offering_id: UUID
    offering_name: str
    periods: list[ReportCardPeriod]
    final_grade: float | None
    recovery_score: float | None
    attendance_rate: float | None
    result: ClassEnrollmentResult
    finalized: bool
    passing_grade: float
    min_attendance: float
