from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.schedule import ClassEnrollmentStatus
from app.schemas.academic_groups import PersonSummary


class RetentionRow(BaseModel):
    class_enrollment_id: UUID
    student: PersonSummary
    status: ClassEnrollmentStatus
    sessions: int
    absences: int
    absence_percent: float
    trailing_absences: int
    level: Literal["ok", "attention", "exceeded"]
    dismissed_at: datetime | None
    dismissal_reason: str | None


class RetentionReportOut(BaseModel):
    class_offering_id: UUID
    offering_name: str
    max_absence_percent: float | None
    rows: list[RetentionRow]


class EvaluationOut(BaseModel):
    dismissed: list[PersonSummary]
