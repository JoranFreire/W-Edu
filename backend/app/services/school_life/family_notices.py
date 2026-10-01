from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import NotificationEventType
from app.models.school_life import AgendaItem, StudentOccurrence
from app.services.guardians.family import FamilyRecipients
from app.services.notifications.events import NotificationEventService
from app.services.school_life.labels import AGENDA_LABELS, OCCURRENCE_LABELS


class FamilyNoticeService:
    """Comunicados da vida escolar ao aluno e a cada responsavel vinculado (caixa de avisos de cada um)."""

    def __init__(self, db: Session):
        self.events = NotificationEventService(db)
        self.family = FamilyRecipients(db)

    def occurrence_registered(self, occurrence: StudentOccurrence) -> None:
        payload = {
            "kind_label": OCCURRENCE_LABELS[occurrence.kind],
            "student_name": occurrence.student.name,
            "occurred_on": occurrence.occurred_on.strftime("%d/%m/%Y"),
        }
        for recipient_id in self.family.of(occurrence.student_id):
            self.events.publish(NotificationEventType.occurrence_registered, payload, recipient_student_id=recipient_id)

    def agenda_published(self, item: AgendaItem, student_ids: list[UUID]) -> None:
        payload = {
            "kind_label": AGENDA_LABELS[item.kind],
            "due_on": item.due_on.strftime("%d/%m/%Y"),
            "title": item.title,
            "class_group_name": item.class_group.name,
        }
        for recipient_id in self.family.of_many(student_ids):
            self.events.publish(NotificationEventType.agenda_published, payload, recipient_student_id=recipient_id)
