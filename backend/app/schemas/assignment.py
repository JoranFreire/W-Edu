from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.assignment import AssignmentSubmissionStatus


class AssignmentSubmissionOut(BaseModel):
    id: UUID
    lesson_id: UUID
    course_id: UUID
    student_id: UUID
    text: str | None
    file_name: str | None
    file_size: int | None
    status: AssignmentSubmissionStatus
    score: int | None
    feedback: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewed_by_id: UUID | None

    model_config = {"from_attributes": True}


class AssignmentReviewIn(BaseModel):
    status: AssignmentSubmissionStatus = AssignmentSubmissionStatus.reviewed
    score: int | None = Field(default=None, ge=0, le=100)
    feedback: str | None = None
