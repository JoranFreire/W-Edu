from uuid import UUID

from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


class Session(TenantMixin, Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    # ID da sessão no BeVox
    bevox_session_id: Mapped[str | None] = mapped_column(String(100), index=True)
    transcript: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["Student"] = relationship(back_populates="sessions")
    lesson: Mapped["Lesson"] = relationship(back_populates="sessions")
    attendance: Mapped[list["Attendance"]] = relationship(back_populates="session")
