from uuid import UUID

from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


class Attendance(TenantMixin, Base):
    __tablename__ = "attendance"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    session_id: Mapped[UUID | None] = mapped_column(ForeignKey("sessions.id"), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="attendance")
    lesson: Mapped["Lesson"] = relationship(back_populates="attendance")
    session: Mapped["Session | None"] = relationship(back_populates="attendance")
