from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.course import CourseModality


class CourseCreate(BaseModel):
    name: str
    description: str | None = None
    modality: CourseModality = CourseModality.online
    agent_id: str | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    modality: CourseModality | None = None
    agent_id: str | None = None


class CourseOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    modality: CourseModality
    agent_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseModuleCreate(BaseModel):
    course_id: UUID | None = None
    title: str
    description: str | None = None
    order: int = 0


class CourseModuleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int | None = None


class CourseModuleOut(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    description: str | None
    order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningPathCreate(BaseModel):
    name: str
    description: str | None = None


class LearningPathUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class LearningPathOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningPathCourseCreate(BaseModel):
    course_id: UUID
    order: int = 0


class LearningPathCourseOut(BaseModel):
    id: UUID
    learning_path_id: UUID
    course_id: UUID
    order: int

    model_config = {"from_attributes": True}


class CoursePrerequisiteCreate(BaseModel):
    prerequisite_course_id: UUID


class CoursePrerequisiteOut(BaseModel):
    id: UUID
    course_id: UUID
    prerequisite_course_id: UUID

    model_config = {"from_attributes": True}


class CourseCompletionRuleOut(BaseModel):
    id: UUID
    course_id: UUID
    require_lessons_complete: bool
    minimum_progress_percent: int
    require_quiz: bool
    minimum_quiz_score: int
    require_attendance: bool
    minimum_attendance_percent: int
    auto_issue: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
