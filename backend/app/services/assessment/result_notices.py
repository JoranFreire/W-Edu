from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import NotificationEventType
from app.models.schedule import ClassEnrollment, ClassOffering
from app.services.assessment.result_rules import RESULT_LABELS
from app.services.guardians.family import FamilyRecipients
from app.services.notifications.events import NotificationEventService


class ResultNoticeService:
    """Aviso de resultado final publicado, ao aluno e aos responsaveis."""

    def __init__(self, db: Session):
        self.events = NotificationEventService(db)
        self.family = FamilyRecipients(db)

    def published(self, offering: ClassOffering, enrollments: list[ClassEnrollment]) -> None:
        for enrollment in enrollments:
            payload = {
                "class_name": offering.name,
                "student_name": enrollment.student.name,
                "result_label": RESULT_LABELS[enrollment.result],
            }
            for recipient_id in self.family.of(enrollment.student_id):
                self.events.publish(
                    NotificationEventType.grades_published, payload, recipient_student_id=recipient_id,
                    class_offering_id=offering.id, course_id=offering.course_id,
                )
