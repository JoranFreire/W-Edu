from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.schedule import ClassEnrollmentResult, ClassEnrollmentStatus, ClassOffering, ClassStatus
from app.models.student import Student
from app.policies.registration_window import ensure_window_open
from app.repositories.registration import StudentRecordRepository, TermOfferingRepository
from app.schemas.course_registration import RegistrationResultOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.registration.access import StudentWindowAccess
from app.services.registration.plan import TermPlanBuilder
from app.services.registration.seats import SeatAllocator
from app.services.registration.waitlist import WaitlistPromotionService
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class SubjectRegistrationService:
    """Inscricao e cancelamento em disciplinas: pelo aluno na janela aberta ou pela secretaria a qualquer tempo."""

    def __init__(self, db: Session):
        self.db = db
        self.access = StudentWindowAccess(db)
        self.plans = TermPlanBuilder(db)
        self.offerings = TermOfferingRepository(db)
        self.records = StudentRecordRepository(db)
        self.seats = SeatAllocator(db)
        self.promotion = WaitlistPromotionService(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def register_in_window(self, student: Student, window_id: int, offering_id: int) -> RegistrationResultOut:
        window, enrollment = self.access.resolve(student, window_id)
        ensure_window_open(window)
        offering = self._offering(offering_id, window.term_id)
        if offering.status != ClassStatus.open:
            raise conflict("A turma não está aberta para matrícula")
        return self._register(enrollment, offering, window.max_credits, window.allow_waitlist, override=False)

    def drop_in_window(self, student: Student, window_id: int, offering_id: int) -> None:
        window, enrollment = self.access.resolve(student, window_id)
        ensure_window_open(window)
        self._drop(enrollment.student_id, self._offering(offering_id, window.term_id))

    def register_by_office(self, program_enrollment_id: int, offering_id: int, override: bool) -> RegistrationResultOut:
        enrollment = self.lifecycle.get_or_404(program_enrollment_id)
        if enrollment.status != ProgramEnrollmentStatus.active:
            raise conflict("A matrícula no programa precisa estar ativa")
        return self._register(enrollment, self._offering(offering_id), None, True, override)

    def drop_by_office(self, program_enrollment_id: int, offering_id: int) -> None:
        enrollment = self.lifecycle.get_or_404(program_enrollment_id)
        self._drop(enrollment.student_id, self._offering(offering_id))

    def _register(
        self, enrollment: ProgramEnrollment, offering: ClassOffering, max_credits: int | None, allow_waitlist: bool, override: bool,
    ) -> RegistrationResultOut:
        offering = self.offerings.lock(offering.id)
        student_id = enrollment.student_id
        current = self.records.enrollment(offering.id, student_id)
        if current is not None and current.status == ClassEnrollmentStatus.active:
            raise conflict("Já inscrito nesta turma")
        if self.records.waitlist_entry(offering.id, student_id):
            raise conflict("Já está na lista de espera desta turma")
        taken = self.offerings.seats_taken([offering.id]).get(offering.id, 0)
        evaluation = self.plans.build(enrollment, offering.term_id, [offering]).evaluate(offering, taken, max_credits)
        if not override:
            if evaluation.blockers:
                raise conflict("; ".join(evaluation.blockers))
            if evaluation.full:
                if not allow_waitlist:
                    raise conflict("Turma lotada")
                entry = self.seats.waitlist(offering.id, student_id)
                self.db.commit()
                return RegistrationResultOut(offering_id=offering.id, result="waitlisted", waitlist_position=self.seats.waitlist_rank(entry))
        self.seats.enroll(offering.id, student_id)
        self.db.commit()
        return RegistrationResultOut(offering_id=offering.id, result="enrolled")

    def _drop(self, student_id: int, offering: ClassOffering) -> None:
        if entry := self.records.waitlist_entry(offering.id, student_id):
            self.db.delete(entry)
            self.db.commit()
            return
        enrollment = self.records.enrollment(offering.id, student_id)
        if enrollment is None or enrollment.status != ClassEnrollmentStatus.active:
            raise not_found("Inscrição não encontrada")
        if enrollment.result != ClassEnrollmentResult.in_progress:
            raise conflict("Disciplina com resultado lançado não pode ser cancelada")
        enrollment.status = ClassEnrollmentStatus.cancelled
        self.db.commit()
        self.promotion.fill(offering)

    def _offering(self, offering_id: int, term_id: int | None = None) -> ClassOffering:
        offering = self.offerings.get_by_id(offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        if offering.subject_id is None or offering.term_id is None:
            raise bad_request("A turma não é oferta de disciplina em período letivo")
        if term_id is not None and offering.term_id != term_id:
            raise bad_request("A turma não é do período desta janela")
        return offering
