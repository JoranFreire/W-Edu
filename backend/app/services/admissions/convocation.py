from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.admissions import AdmissionApplication, AdmissionCall, ApplicationStatus, SeatKind
from app.models.notification import NotificationEventType
from app.models.student import Student
from app.repositories.admissions import AdmissionApplicationRepository
from app.schemas.admissions import ApplicationOut, DeadlinesOut
from app.services.academic.errors import conflict
from app.services.admissions.applications import ApplicationService
from app.services.admissions.calls import AdmissionCallService
from app.services.admissions.rules import Candidate, fill
from app.services.admissions.views import application_out
from app.services.notifications.events import NotificationEventService
from app.services.registration.rules import as_utc
from app.services.registration.seats import SeatAllocator

OCCUPYING = (ApplicationStatus.selected, ApplicationStatus.confirmed)


def candidate(application: AdmissionApplication) -> Candidate:
    """A reserva vale para quem a declarou, salvo se a conferencia a recusou."""
    reserved = application.claims_reserved and application.reserved_verified is not False
    return Candidate(application.id, application.created_at, application.review_score, reserved)


class ConvocationService:
    """Convocacao com prazo de confirmacao, matricula na turma, desistencia e chamadas sucessivas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AdmissionApplicationRepository(db)
        self.calls = AdmissionCallService(db)
        self.applicant_side = ApplicationService(db)
        self.seats = SeatAllocator(db)
        self.notices = NotificationEventService(db)

    def summon(self, call: AdmissionCall, chosen: list[tuple[Candidate, SeatKind]]) -> int:
        by_id = {application.id: application for application in self.repo.list_by_call(call.id)}
        now = datetime.now(timezone.utc)
        summoned = []
        for item, kind in chosen:
            application = by_id[item.id]
            application.status, application.seat_kind = ApplicationStatus.selected, kind
            application.called_at, application.confirm_until = now, now + timedelta(days=call.confirmation_days)
            summoned.append(application)
        self.db.commit()
        for application in summoned:
            self.notices.publish(
                NotificationEventType.admission_called,
                {"protocol": application.protocol, "call_title": call.title, "confirm_until": application.confirm_until.strftime("%d/%m/%Y")},
                recipient_student_id=application.applicant_id,
            )
        return len(summoned)

    def confirm(self, applicant: Student, application_id: int) -> ApplicationOut:
        application = self.applicant_side.own(applicant, application_id)
        if application.status != ApplicationStatus.selected:
            raise conflict("Inscrição não está convocada")
        if as_utc(application.confirm_until) < datetime.now(timezone.utc):
            self.process_deadlines(application.call_id)
            raise conflict("Prazo de confirmação encerrado")
        self.seats.enroll(application.call.class_offering_id, applicant.id)
        application.status, application.confirmed_at = ApplicationStatus.confirmed, datetime.now(timezone.utc)
        return application_out(self.repo.save(application))

    def decline(self, applicant: Student, application_id: int) -> ApplicationOut:
        application = self.applicant_side.own(applicant, application_id)
        if application.status not in (ApplicationStatus.selected, ApplicationStatus.waitlisted):
            raise conflict("Só se desiste de vaga convocada ou em espera")
        was_called = application.status == ApplicationStatus.selected
        application.status = ApplicationStatus.declined
        self.db.commit()
        if was_called:
            self.call_next(application.call)
        return application_out(application)

    def process_deadlines(self, call_id: int) -> DeadlinesOut:
        """Expira quem nao confirmou no prazo e chama os proximos da lista."""
        call = self.calls.get_or_404(call_id)
        now = datetime.now(timezone.utc)
        expired = [a for a in self.repo.with_status(call.id, (ApplicationStatus.selected,)) if as_utc(a.confirm_until) < now]
        for application in expired:
            application.status = ApplicationStatus.expired
        self.db.commit()
        called = self.call_next(call)
        return DeadlinesOut(expired=len(expired), called=called, waitlisted=len(self.repo.with_status(call.id, (ApplicationStatus.waitlisted,))))

    def call_next(self, call: AdmissionCall) -> int:
        occupying = self.repo.with_status(call.id, OCCUPYING)
        free = call.seats - len(occupying)
        if free <= 0:
            return 0
        reserved_taken = sum(1 for a in occupying if a.seat_kind == SeatKind.reserved)
        reserved_free = min(max(call.reserved_seats - reserved_taken, 0), free)
        waitlist = [candidate(a) for a in self.repo.with_status(call.id, (ApplicationStatus.waitlisted,))]
        return self.summon(call, fill(waitlist, reserved_free, free - reserved_free))
