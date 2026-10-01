from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.progress import ProgressStatus


class ProgressUpdate(BaseModel):
    status: ProgressStatus


class ProgressOut(BaseModel):
    id: UUID
    student_id: UUID
    lesson_id: UUID
    status: ProgressStatus
    content_consumed_at: Optional[datetime]
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourseProgressOut(BaseModel):
    course_id: UUID
    course_name: str
    total_lessons: int
    done_lessons: int
    in_progress_lessons: int
    pending_lessons: int
    progress_percent: int
    last_activity_at: Optional[datetime] = None
