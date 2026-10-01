from datetime import datetime, timezone
import enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.tenancy import TenantMixin


class NotificationChannel(str, enum.Enum):
    internal = "internal"
    whatsapp = "whatsapp"
    email = "email"
    push = "push"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class NotificationEventType(str, enum.Enum):
    class_created = "class_created"
    meeting_created = "meeting_created"
    meeting_reminder = "meeting_reminder"
    absence_registered = "absence_registered"
    attendance_recorded = "attendance_recorded"
    content_published = "content_published"
    certificate_issued = "certificate_issued"
    grades_published = "grades_published"
    occurrence_registered = "occurrence_registered"
    agenda_published = "agenda_published"
    waitlist_promoted = "waitlist_promoted"
    activity_reviewed = "activity_reviewed"
    admission_called = "admission_called"
    absence_dismissal = "absence_dismissal"
    material_request_decided = "material_request_decided"


class NotificationTemplate(TenantMixin, Base):
    __tablename__ = "notification_templates"
    __table_args__ = (UniqueConstraint("institution_id", "key", "channel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), default=NotificationChannel.internal)
    title_template: Mapped[str] = mapped_column(String(200))
    body_template: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class NotificationEvent(TenantMixin, Base):
    __tablename__ = "notification_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[NotificationEventType] = mapped_column(SAEnum(NotificationEventType), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), default=NotificationChannel.internal)
    template_key: Mapped[str | None] = mapped_column(String(120), index=True)
    recipient_student_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id"), nullable=True, index=True)
    class_offering_id: Mapped[int | None] = mapped_column(ForeignKey("class_offerings.id"), nullable=True, index=True)
    scheduled_meeting_id: Mapped[int | None] = mapped_column(ForeignKey("scheduled_meetings.id"), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationStatus] = mapped_column(SAEnum(NotificationStatus), default=NotificationStatus.pending)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text)
    # Leitura pelo destinatario na caixa de avisos (canal interno).
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
