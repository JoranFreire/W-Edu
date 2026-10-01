from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class AttendanceOut(BaseModel):
    id: UUID
    student_id: UUID
    lesson_id: UUID
    session_id: UUID | None
    recorded_at: datetime

    model_config = {"from_attributes": True}
