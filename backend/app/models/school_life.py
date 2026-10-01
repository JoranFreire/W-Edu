"""Vida escolar (escola basica): ocorrencias do aluno e agenda da turma."""

from uuid import UUID

from app.core.ids import new_id
from datetime import date, datetime, timezone
import enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OccurrenceKind(str, enum.Enum):
    behavior = "behavior"      # comportamento/disciplinar
    lateness = "lateness"      # atraso
    material = "material"      # falta de material/uniforme
    health = "health"          # saude/bem-estar
    merit = "merit"            # elogio
    other = "other"


class OccurrenceSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AgendaItemKind(str, enum.Enum):
    homework = "homework"
    test = "test"
    event = "event"
    notice = "notice"


class StudentOccurrence(TenantMixin, Base):
    __tablename__ = "student_occurrences"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    class_group_id: Mapped[UUID | None] = mapped_column(ForeignKey("class_groups.id"), index=True)
    kind: Mapped[OccurrenceKind] = mapped_column(SAEnum(OccurrenceKind), default=OccurrenceKind.other)
    severity: Mapped[OccurrenceSeverity] = mapped_column(SAEnum(OccurrenceSeverity), default=OccurrenceSeverity.low)
    description: Mapped[str] = mapped_column(Text)
    occurred_on: Mapped[date] = mapped_column(Date, index=True)
    reported_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    # Ciencia do responsavel (quem e quando), registrada no portal.
    acknowledged_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    student: Mapped["Student"] = relationship(foreign_keys=[student_id])
    reported_by: Mapped["Student | None"] = relationship(foreign_keys=[reported_by_id])


class AgendaItem(TenantMixin, Base):
    __tablename__ = "agenda_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    class_group_id: Mapped[UUID] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), index=True)
    class_offering_id: Mapped[UUID | None] = mapped_column(ForeignKey("class_offerings.id"), index=True)
    kind: Mapped[AgendaItemKind] = mapped_column(SAEnum(AgendaItemKind), default=AgendaItemKind.homework)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    due_on: Mapped[date] = mapped_column(Date, index=True)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    class_group: Mapped["ClassGroup"] = relationship()
    class_offering: Mapped["ClassOffering | None"] = relationship()
