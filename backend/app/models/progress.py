from uuid import UUID

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import ForeignKey, DateTime, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


class ProgressStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class Progress(TenantMixin, Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("student_id", "lesson_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    status: Mapped[ProgressStatus] = mapped_column(SAEnum(ProgressStatus), default=ProgressStatus.pending)
    content_consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    student: Mapped["Student"] = relationship(back_populates="progress")
    lesson: Mapped["Lesson"] = relationship(back_populates="progress")
