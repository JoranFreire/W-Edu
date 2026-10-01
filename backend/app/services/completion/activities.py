from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.completion import ComplementaryActivity, ReviewStatus
from app.models.notification import NotificationEventType
from app.models.student import Student
from app.policies.completion_access import ensure_active, ensure_own
from app.repositories.completion import ComplementaryActivityRepository
from app.schemas.completion import ActivityCreate, ActivityDecision
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.completion.enrollments import OwnEnrollmentLookup
from app.services.completion.labels import REVIEW_LABELS
from app.services.notifications.events import NotificationEventService
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class ComplementaryActivityService:
    """Atividades complementares: o aluno declara, a secretaria aprova as horas que valem."""

    def __init__(self, db: Session):
        self.repo = ComplementaryActivityRepository(db)
        self.own = OwnEnrollmentLookup(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.notices = NotificationEventService(db)

    def list_for_enrollment(self, enrollment_id: UUID) -> list[ComplementaryActivity]:
        self.lifecycle.get_or_404(enrollment_id)
        return self.repo.list_by_enrollment(enrollment_id)

    def list_mine(self, student: Student) -> list[ComplementaryActivity]:
        return self.repo.list_by_student(student.id)

    def submit(self, student: Student, enrollment_id: UUID, data: ActivityCreate) -> ComplementaryActivity:
        enrollment = self.own.get(student, enrollment_id)
        ensure_active(enrollment)
        return self.repo.save(ComplementaryActivity(program_enrollment_id=enrollment.id, **data.model_dump()))

    def withdraw(self, student: Student, activity_id: UUID) -> None:
        activity = self._get_or_404(activity_id)
        ensure_own(activity.program_enrollment, student)
        if activity.status != ReviewStatus.submitted:
            raise conflict("Atividade já avaliada")
        self.repo.delete(activity)

    def decide(self, activity_id: UUID, data: ActivityDecision, reviewer: Student) -> ComplementaryActivity:
        activity = self._get_or_404(activity_id)
        if activity.status != ReviewStatus.submitted:
            raise conflict("Atividade já avaliada")
        hours = data.hours_approved or activity.hours_requested
        if data.approved and hours > activity.hours_requested:
            raise bad_request("As horas aprovadas não podem passar das solicitadas")
        activity.status = ReviewStatus.approved if data.approved else ReviewStatus.rejected
        activity.hours_approved = hours if data.approved else None
        activity.decision_note, activity.decided_by_id, activity.decided_at = data.note, reviewer.id, datetime.now(timezone.utc)
        saved = self.repo.save(activity)
        self.notices.publish(
            NotificationEventType.activity_reviewed,
            {"title": activity.title, "status_label": REVIEW_LABELS[activity.status], "hours": activity.hours_approved or 0},
            recipient_student_id=activity.program_enrollment.student_id,
        )
        return saved

    def _get_or_404(self, activity_id: UUID) -> ComplementaryActivity:
        activity = self.repo.get_by_id(activity_id)
        if not activity:
            raise not_found("Atividade não encontrada")
        return activity
