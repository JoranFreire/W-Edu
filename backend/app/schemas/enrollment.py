from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    student_id: UUID
    course_id: UUID


class EnrollmentOut(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    enrolled_at: datetime

    model_config = {"from_attributes": True}
