from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import NotificationEventType
from app.models.schedule import ClassEnrollmentStatus, ClassOffering
from app.models.student import Student
from app.policies.retention_access import ensure_can_follow
from app.repositories.retention import RetentionEnrollmentRepository
from app.repositories.schedule import ClassOfferingRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.retention import EvaluationOut, RetentionReportOut, RetentionRow
from app.services.academic.errors import conflict, not_found
from app.services.notifications.events import NotificationEventService
from app.services.retention.ledger import AttendanceLedgerBuilder
from app.services.retention.rules import DEFAULT_LIMIT_PERCENT, level


class RetentionService:
    """Frequencia e risco de evasao por aluno; desliga quem passa do limite de faltas da turma (quando definido)."""

    def __init__(self, db: Session):
        self.db = db
        self.offerings = ClassOfferingRepository(db)
        self.enrollments = RetentionEnrollmentRepository(db)
        self.ledgers = AttendanceLedgerBuilder(db)
        self.notices = NotificationEventService(db)

    def report(self, offering_id: int, user: Student) -> RetentionReportOut:
        offering = self._offering(offering_id)
        ensure_can_follow(user, offering)
        tracked = self.enrollments.tracked(offering.id)
        ledgers = self.ledgers.for_enrollments(offering.id, tracked)
        rows = [
            RetentionRow(
                class_enrollment_id=e.id, student=PersonSummary.model_validate(e.student), status=e.status,
                sessions=ledgers[e.id].total, absences=ledgers[e.id].absences, absence_percent=ledgers[e.id].absence_percent,
                trailing_absences=ledgers[e.id].trailing_absences, level=level(ledgers[e.id], offering.max_absence_percent),
                dismissed_at=e.dismissed_at, dismissal_reason=e.dismissal_reason,
            )
            for e in tracked
        ]
        rows.sort(key=lambda row: (row.dismissed_at is not None, -row.absence_percent))
        return RetentionReportOut(class_offering_id=offering.id, offering_name=offering.name, max_absence_percent=offering.max_absence_percent, rows=rows)

    def evaluate(self, offering_id: int) -> EvaluationOut:
        return EvaluationOut(dismissed=[PersonSummary.model_validate(s) for s in self.dismiss_exceeded(self._offering(offering_id))])

    def dismiss_exceeded(self, offering: ClassOffering) -> list[Student]:
        """Desliga os ativos acima do limite; sem limite definido na turma, ninguem e desligado."""
        if offering.max_absence_percent is None:
            return []
        active = [e for e in self.enrollments.tracked(offering.id) if e.status == ClassEnrollmentStatus.active]
        ledgers = self.ledgers.for_enrollments(offering.id, active)
        now, dismissed = datetime.now(timezone.utc), []
        for enrollment in active:
            ledger = ledgers[enrollment.id]
            if level(ledger, offering.max_absence_percent) != "exceeded":
                continue
            enrollment.status, enrollment.dismissed_at = ClassEnrollmentStatus.cancelled, now
            enrollment.dismissal_reason = (
                f"{ledger.absences} falta(s) em {max(ledger.planned, ledger.total)} sessões previstas (limite {offering.max_absence_percent:g}%)"
            )
            dismissed.append((enrollment.student, ledger.absence_percent))
        self.db.commit()
        for student, percent in dismissed:
            self.notices.publish(
                NotificationEventType.absence_dismissal,
                {"class_name": offering.name, "absence_percent": f"{percent:g}", "limit": f"{offering.max_absence_percent:g}"},
                recipient_student_id=student.id, class_offering_id=offering.id, course_id=offering.course_id,
            )
        return [student for student, _ in dismissed]

    def readmit(self, enrollment_id: int) -> RetentionRow:
        enrollment = self.enrollments.get(enrollment_id)
        if not enrollment:
            raise not_found("Inscrição não encontrada")
        if enrollment.dismissed_at is None:
            raise conflict("A inscrição não foi desligada")
        enrollment.status, enrollment.dismissed_at, enrollment.dismissal_reason = ClassEnrollmentStatus.active, None, None
        self.db.commit()
        ledger = self.ledgers.for_enrollments(enrollment.class_offering_id, [enrollment])[enrollment.id]
        return RetentionRow(
            class_enrollment_id=enrollment.id, student=PersonSummary.model_validate(enrollment.student), status=enrollment.status,
            sessions=ledger.total, absences=ledger.absences, absence_percent=ledger.absence_percent, trailing_absences=ledger.trailing_absences,
            level=level(ledger, enrollment.class_offering.max_absence_percent or DEFAULT_LIMIT_PERCENT), dismissed_at=None, dismissal_reason=None,
        )

    def _offering(self, offering_id: int) -> ClassOffering:
        offering = self.offerings.get_by_id(offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        return offering
