from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.notification import NotificationEventType
from app.models.schedule import ClassOffering
from app.repositories.academic import ProgramEnrollmentRepository
from app.repositories.registration import TermOfferingRepository
from app.services.notifications.events import NotificationEventService
from app.services.registration.plan import TermPlanBuilder
from app.services.registration.seats import SeatAllocator


class WaitlistPromotionService:
    """Ao abrir vaga, inscreve os primeiros da lista de espera que continuam aptos (pre-requisito e horario)."""

    def __init__(self, db: Session):
        self.db = db
        self.offerings = TermOfferingRepository(db)
        self.enrollments = ProgramEnrollmentRepository(db)
        self.plans = TermPlanBuilder(db)
        self.seats = SeatAllocator(db)
        self.notices = NotificationEventService(db)

    def fill(self, offering: ClassOffering) -> list[UUID]:
        free = offering.capacity - self.offerings.seats_taken([offering.id]).get(offering.id, 0)
        promoted = []
        for entry in self.offerings.waitlist(offering.id):
            if free <= 0:
                break
            enrollment = self._program_enrollment(entry.student_id, offering.subject_id)
            if enrollment is None or self.plans.build(enrollment, offering.term_id, [offering]).evaluate(offering, 0, None).blockers:
                continue
            self.db.delete(entry)
            self.seats.enroll(offering.id, entry.student_id)
            promoted.append(entry.student_id)
            free -= 1
        self.db.commit()
        for student_id in promoted:
            self.notices.publish(
                NotificationEventType.waitlist_promoted,
                {"offering_name": offering.name, "subject_name": offering.subject.name if offering.subject else offering.name},
                recipient_student_id=student_id, class_offering_id=offering.id, course_id=offering.course_id,
            )
        return promoted

    def _program_enrollment(self, student_id: UUID, subject_id: UUID | None) -> ProgramEnrollment | None:
        """Matricula ativa cuja matriz tem a disciplina (senao, a primeira ativa)."""
        active = self.enrollments.list(student_id=student_id, status=ProgramEnrollmentStatus.active)
        with_subject = [e for e in active if any(c.subject_id == subject_id for c in e.curriculum.components)]
        return (with_subject or active or [None])[0]
