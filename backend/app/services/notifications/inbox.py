from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import NotificationEvent
from app.models.student import Student
from app.repositories.notification import NotificationInboxRepository
from app.schemas.notification import InboxSummaryOut
from app.services.academic.errors import not_found


class NotificationInboxService:
    """Caixa de avisos do usuario: comunicados internos enderecados a ele na instituicao ativa."""

    def __init__(self, db: Session):
        self.repo = NotificationInboxRepository(db)

    def list(self, user: Student, unread_only: bool = False, limit: int = 50) -> list[NotificationEvent]:
        return self.repo.list_for(user.id, unread_only=unread_only, limit=min(max(limit, 1), 200))

    def summary(self, user: Student) -> InboxSummaryOut:
        return InboxSummaryOut(unread=self.repo.unread_count(user.id))

    def mark_read(self, user: Student, event_id: UUID) -> NotificationEvent:
        event = self.repo.get_for(user.id, event_id)
        if not event:
            raise not_found("Aviso não encontrado")
        if event.read_at is None:
            event.read_at = datetime.now(timezone.utc)
            self.repo.db.commit()
        return event

    def mark_all_read(self, user: Student) -> InboxSummaryOut:
        self.repo.mark_all_read(user.id, datetime.now(timezone.utc))
        return self.summary(user)
