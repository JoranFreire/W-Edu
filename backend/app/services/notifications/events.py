from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import NotificationChannel, NotificationEvent, NotificationEventType, NotificationStatus
from app.repositories.notification import NotificationEventRepository
from app.schemas.notification import NotificationEventCreate
from app.services.notifications.templates import NotificationTemplateService, render_template


class NotificationEventService:
    """Publicacao e acompanhamento de eventos de notificacao."""

    def __init__(self, db: Session):
        self.repo = NotificationEventRepository(db)
        self.templates = NotificationTemplateService(db)

    def list(self, limit: int = 100) -> list[NotificationEvent]:
        self.templates.ensure_defaults()
        return self.repo.list_all(limit=limit)

    def publish(
        self,
        event_type: NotificationEventType,
        payload: dict,
        *,
        channel: NotificationChannel = NotificationChannel.internal,
        template_key: str | None = None,
        recipient_student_id: int | None = None,
        course_id: int | None = None,
        class_offering_id: int | None = None,
        scheduled_meeting_id: int | None = None,
        scheduled_for: datetime | None = None,
    ) -> NotificationEvent:
        key = template_key or event_type.value
        template = self.templates.get_for(key, channel)
        now = datetime.now(timezone.utc)
        # Evento interno imediato ja nasce enviado; demais canais e agendados aguardam a entrega.
        scheduled_in_future = scheduled_for is not None and scheduled_for > now
        status_value = (
            NotificationStatus.sent
            if channel == NotificationChannel.internal and not scheduled_in_future
            else NotificationStatus.pending
        )
        return self.repo.create(NotificationEvent(
            event_type=event_type,
            channel=channel,
            template_key=key,
            recipient_student_id=recipient_student_id,
            course_id=course_id,
            class_offering_id=class_offering_id,
            scheduled_meeting_id=scheduled_meeting_id,
            payload=payload,
            title=render_template(template.title_template, payload),
            body=render_template(template.body_template, payload),
            status=status_value,
            scheduled_for=scheduled_for,
            sent_at=now if status_value == NotificationStatus.sent else None,
        ))

    def create(self, data: NotificationEventCreate) -> NotificationEvent:
        return self.publish(
            data.event_type,
            data.payload,
            channel=data.channel,
            template_key=data.template_key,
            recipient_student_id=data.recipient_student_id,
            course_id=data.course_id,
            class_offering_id=data.class_offering_id,
            scheduled_meeting_id=data.scheduled_meeting_id,
            scheduled_for=data.scheduled_for,
        )

    def retry(self, event_id: int) -> NotificationEvent:
        """Devolve um evento que falhou para a fila; o worker tenta entregar de novo."""
        event = self._get_or_404(event_id)
        if event.status != NotificationStatus.failed:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Só eventos com falha podem ser reenviados")
        event.status = NotificationStatus.pending
        event.error_message = None
        return self.repo.update(event)

    def _get_or_404(self, event_id: int) -> NotificationEvent:
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado")
        return event
