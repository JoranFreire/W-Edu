"""Diario de classe: conteudo ministrado e frequencia por aula da oferta."""

from uuid import UUID

from app.core.ids import new_id
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ClassDiaryEntry(TenantMixin, Base):
    __tablename__ = "class_diary_entries"
    __table_args__ = (UniqueConstraint("class_offering_id", "date"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    class_offering_id: Mapped[UUID] = mapped_column(ForeignKey("class_offerings.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date)
    # Aulas (horas-aula) do dia; cada falta conta por aula.
    lesson_count: Mapped[int] = mapped_column(Integer, default=1)
    content_taught: Mapped[str] = mapped_column(Text)
    instructor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    scheduled_meeting_id: Mapped[UUID | None] = mapped_column(ForeignKey("scheduled_meetings.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    attendance: Mapped[list["DiaryAttendance"]] = relationship(back_populates="entry", cascade="all, delete-orphan")


class DiaryAttendance(TenantMixin, Base):
    __tablename__ = "diary_attendance"
    __table_args__ = (UniqueConstraint("diary_entry_id", "class_enrollment_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    diary_entry_id: Mapped[UUID] = mapped_column(ForeignKey("class_diary_entries.id", ondelete="CASCADE"), index=True)
    class_enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("class_enrollments.id"), index=True)
    absences: Mapped[int] = mapped_column(Integer, default=0)
    justified: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(String(300))

    entry: Mapped["ClassDiaryEntry"] = relationship(back_populates="attendance")
