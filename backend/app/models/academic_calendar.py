"""Calendario academico: periodos letivos, etapas de avaliacao e eventos."""

from uuid import UUID

from datetime import date, datetime, timezone
import enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TermKind(str, enum.Enum):
    year = "year"            # ano letivo
    semester = "semester"
    quarter = "quarter"
    module = "module"


class TermStatus(str, enum.Enum):
    planned = "planned"
    open = "open"
    closed = "closed"


class GradingPeriodStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class CalendarEventKind(str, enum.Enum):
    school_day = "school_day"    # dia letivo extra (ex.: sabado letivo)
    holiday = "holiday"
    recess = "recess"
    exam = "exam"
    event = "event"


class AcademicTerm(TenantMixin, Base):
    __tablename__ = "academic_terms"
    __table_args__ = (UniqueConstraint("institution_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(80))
    kind: Mapped[TermKind] = mapped_column(SAEnum(TermKind), default=TermKind.semester)
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    status: Mapped[TermStatus] = mapped_column(SAEnum(TermStatus), default=TermStatus.planned)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    grading_periods: Mapped[list["GradingPeriod"]] = relationship(
        back_populates="term", order_by="GradingPeriod.order", cascade="all, delete-orphan"
    )


class GradingPeriod(TenantMixin, Base):
    __tablename__ = "grading_periods"
    __table_args__ = (UniqueConstraint("term_id", "order"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    term_id: Mapped[UUID] = mapped_column(ForeignKey("academic_terms.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    order: Mapped[int] = mapped_column(Integer)
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    weight: Mapped[float] = mapped_column(Float, default=1)
    status: Mapped[GradingPeriodStatus] = mapped_column(SAEnum(GradingPeriodStatus), default=GradingPeriodStatus.open)

    term: Mapped["AcademicTerm"] = relationship(back_populates="grading_periods")


class CalendarEvent(TenantMixin, Base):
    __tablename__ = "calendar_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    term_id: Mapped[UUID | None] = mapped_column(ForeignKey("academic_terms.id", ondelete="CASCADE"), index=True)
    kind: Mapped[CalendarEventKind] = mapped_column(SAEnum(CalendarEventKind))
    title: Mapped[str] = mapped_column(String(200))
    starts_on: Mapped[date] = mapped_column(Date, index=True)
    # Vazio = evento de um dia; preenchido = intervalo inclusivo (ex.: recesso).
    ends_on: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
