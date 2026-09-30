from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import NotificationEventType
from app.models.school_life import AgendaItem, StudentOccurrence
from app.services.notifications.events import NotificationEventService
from app.services.school_life.labels import AGENDA_LABELS, OCCURRENCE_LABELS


class FamilyNoticeService:
    """Comunicados da vida escolar, enderecados ao aluno (o portal do responsavel os exibe)."""

    def __init__(self, db: Session):
        self.events = NotificationEventService(db)

    def occurrence_registered(self, occurrence: StudentOccurrence) -> None:
        self.events.publish(
            NotificationEventType.occurrence_registered,
            {
                "kind_label": OCCURRENCE_LABELS[occurrence.kind],
                "student_name": occurrence.student.name,
                "occurred_on": occurrence.occurred_on.strftime("%d/%m/%Y"),
            },
            recipient_student_id=occurrence.student_id,
        )

    def agenda_published(self, item: AgendaItem, student_ids: list[int]) -> None:
        payload = {
            "kind_label": AGENDA_LABELS[item.kind],
            "due_on": item.due_on.strftime("%d/%m/%Y"),
            "title": item.title,
            "class_group_name": item.class_group.name,
        }
        for student_id in student_ids:
            self.events.publish(NotificationEventType.agenda_published, payload, recipient_student_id=student_id)
