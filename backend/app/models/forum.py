from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


class ForumThread(TenantMixin, Base):
    __tablename__ = "forum_threads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    course: Mapped["Course"] = relationship()
    author: Mapped["Student"] = relationship()
    posts: Mapped[list["ForumPost"]] = relationship(
        back_populates="thread",
        order_by="ForumPost.created_at",
        cascade="all, delete-orphan",
    )


class ForumPost(TenantMixin, Base):
    __tablename__ = "forum_posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    thread_id: Mapped[UUID] = mapped_column(ForeignKey("forum_threads.id"), index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    thread: Mapped["ForumThread"] = relationship(back_populates="posts")
    author: Mapped["Student"] = relationship()
