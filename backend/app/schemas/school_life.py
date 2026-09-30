from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.school_life import AgendaItemKind, OccurrenceKind, OccurrenceSeverity
from app.schemas.academic_groups import PersonSummary


class OccurrenceCreate(BaseModel):
    student_id: int
    class_group_id: int | None = None
    kind: OccurrenceKind = OccurrenceKind.other
    severity: OccurrenceSeverity = OccurrenceSeverity.low
    description: str = Field(min_length=1, max_length=4000)
    occurred_on: date | None = None


class OccurrenceOut(BaseModel):
    id: int
    student: PersonSummary
    class_group_id: int | None
    kind: OccurrenceKind
    severity: OccurrenceSeverity
    description: str
    occurred_on: date
    reported_by: PersonSummary | None
    acknowledged_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AgendaItemCreate(BaseModel):
    kind: AgendaItemKind = AgendaItemKind.homework
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    due_on: date
    class_offering_id: int | None = None


class AgendaItemOut(BaseModel):
    id: int
    class_group_id: int
    class_group_name: str
    class_offering_id: int | None
    class_offering_name: str | None
    kind: AgendaItemKind
    title: str
    description: str | None
    due_on: date
    created_at: datetime
