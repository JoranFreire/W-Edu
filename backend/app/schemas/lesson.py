from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.lesson import LessonType


class LessonCreate(BaseModel):
    course_id: UUID
    module_id: UUID | None = None
    title: str
    content: str | None = None
    order: int = 0
    type: LessonType = LessonType.text
    video_url: str | None = None


class LessonUpdate(BaseModel):
    module_id: UUID | None = None
    title: str | None = None
    content: str | None = None
    order: int | None = None
    type: LessonType | None = None
    video_url: str | None = None


class LessonOut(BaseModel):
    id: UUID
    course_id: UUID
    module_id: UUID | None
    title: str
    content: str | None
    order: int
    type: LessonType
    video_url: str | None
    has_video_file: bool
    created_at: datetime

    model_config = {"from_attributes": True}
