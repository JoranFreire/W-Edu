from uuid import UUID

from app.core.ids import new_id
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


class ChatConversation(TenantMixin, Base):
    __tablename__ = "chat_conversations"
    __table_args__ = (UniqueConstraint("course_id", "student_id", "instructor_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    instructor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    subject: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    course: Mapped["Course"] = relationship()
    student: Mapped["Student"] = relationship(foreign_keys=[student_id])
    instructor: Mapped["Student | None"] = relationship(foreign_keys=[instructor_id])
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        order_by="ChatMessage.created_at",
        cascade="all, delete-orphan",
    )


class ChatMessage(TenantMixin, Base):
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("chat_conversations.id"), index=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")
    sender: Mapped["Student"] = relationship()
