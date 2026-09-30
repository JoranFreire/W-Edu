from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import NotificationChannel, NotificationEvent, NotificationStatus
from app.repositories.notification import NotificationEventRepository
from app.services.notifications.channels import EmailChannel, WhatsAppChannel


class NotificationDeliveryService:
    """Entrega eventos pendentes pelos canais externos (usado pelo worker e pela rota manual)."""

    def __init__(self, db: Session):
        self.repo = NotificationEventRepository(db)
        self.channels = {
            NotificationChannel.whatsapp: WhatsAppChannel(db),
            NotificationChannel.email: EmailChannel(db),
        }

    def process_due(self, limit: int = 100) -> list[NotificationEvent]:
        events = self.repo.list_ready(datetime.now(timezone.utc), limit=limit)
        for event in events:
            try:
                self._dispatch(event)
                event.status = NotificationStatus.sent
                event.sent_at = datetime.now(timezone.utc)
                event.error_message = None
            except Exception as exc:
                event.status = NotificationStatus.failed
                event.error_message = str(exc)
            self.repo.update(event)
        return events

    def _dispatch(self, event: NotificationEvent) -> None:
        if event.channel == NotificationChannel.internal:
            return
        channel = self.channels.get(event.channel)
        if not channel:
            raise RuntimeError(f"Canal {event.channel.value} ainda não possui adaptador configurado")
        channel.send(event)
