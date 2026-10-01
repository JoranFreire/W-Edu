from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.course_registration import RegistrationWindow
from app.models.schedule import ClassOffering
from app.models.student import Student
from app.repositories.academic import AcademicTermRepository
from app.repositories.registration import OfferingTimeSlotRepository, TermOfferingRepository
from app.schemas.academic import SubjectSummary
from app.schemas.course_registration import CatalogOffering, RegistrationCatalogOut, TimeSlotOut
from app.services.academic.errors import not_found
from app.services.registration.access import StudentWindowAccess
from app.services.registration.plan import TermPlan, TermPlanBuilder
from app.services.registration.seats import SeatAllocator
from app.services.registration.windows import to_out
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class RegistrationCatalogService:
    """Ofertas do periodo para as disciplinas da matriz do aluno, com a situacao de cada uma."""

    def __init__(self, db: Session):
        self.access = StudentWindowAccess(db)
        self.plans = TermPlanBuilder(db)
        self.offerings = TermOfferingRepository(db)
        self.slots = OfferingTimeSlotRepository(db)
        self.seats = SeatAllocator(db)
        self.terms = AcademicTermRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def for_window(self, student: Student, window_id: int) -> RegistrationCatalogOut:
        window, enrollment = self.access.resolve(student, window_id)
        return self._build(enrollment, window.term_id, window)

    def for_enrollment(self, program_enrollment_id: int, term_id: int) -> RegistrationCatalogOut:
        """Visao da secretaria, sem janela (sem limite de creditos)."""
        enrollment = self.lifecycle.get_or_404(program_enrollment_id)
        if not self.terms.get_by_id(term_id):
            raise not_found("Período letivo não encontrado")
        return self._build(enrollment, term_id, None)

    def _build(self, enrollment: ProgramEnrollment, term_id: int, window: RegistrationWindow | None) -> RegistrationCatalogOut:
        curriculum_subjects = {component.subject_id for component in enrollment.curriculum.components}
        offered = self.offerings.open_for_subjects(term_id, curriculum_subjects)
        plan = self.plans.build(enrollment, term_id, offered)
        # Inscricoes do periodo fora da matriz (ex.: feitas pela secretaria) tambem aparecem.
        offerings = {offering.id: offering for offering in [*offered, *plan.enrolled.values()] if offering.subject_id}
        seats = self.offerings.seats_taken(list(offerings))
        slots = self.slots.by_offerings(list(offerings))
        max_credits = window.max_credits if window else None
        allow_waitlist = window.allow_waitlist if window else True
        items = [
            self._item(plan, offering, seats.get(offering.id, 0), slots.get(offering.id, []), max_credits, allow_waitlist)
            for offering in offerings.values()
        ]
        items.sort(key=lambda item: (item.term_number or 99, item.subject.code, item.offering_name))
        return RegistrationCatalogOut(
            window=to_out(window) if window else None, term_id=term_id, program_enrollment_id=enrollment.id,
            registration_number=enrollment.registration_number, program_name=enrollment.program.name,
            credits_registered=plan.registered_credits(), min_credits=window.min_credits if window else None,
            max_credits=max_credits, offerings=items,
        )

    def _item(self, plan: TermPlan, offering: ClassOffering, taken: int, slots: list, max_credits: int | None, allow_waitlist: bool) -> CatalogOffering:
        component = plan.components.get(offering.subject_id)
        situation, blockers, position = "available", [], None
        if offering.id in plan.enrolled:
            situation = "enrolled"
        elif offering.id in plan.waitlisted:
            situation, position = "waitlisted", self.seats.waitlist_rank(plan.waitlisted[offering.id])
        else:
            evaluation = plan.evaluate(offering, taken, max_credits)
            blockers = evaluation.blockers
            if evaluation.full and not allow_waitlist:
                blockers = [*blockers, "Turma lotada"]
            situation = "blocked" if blockers else "full" if evaluation.full else "available"
        return CatalogOffering(
            offering_id=offering.id, offering_name=offering.name, subject=SubjectSummary.model_validate(offering.subject),
            term_number=component.term_number if component else None, kind=component.kind if component else None,
            credits=plan.credit_of(offering), instructor_name=offering.instructor.name if offering.instructor else None,
            slots=[TimeSlotOut.model_validate(slot) for slot in slots], capacity=offering.capacity, seats_taken=taken,
            situation=situation, waitlist_position=position, blockers=blockers,
        )
