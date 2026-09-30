from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_calendar import GradingPeriod
from app.models.assessment import OfferingPeriodClosure, PeriodResult
from app.models.schedule import ClassEnrollmentResult, ClassOffering
from app.models.student import Student
from app.policies.assessment_locks import ensure_offering_open
from app.repositories.academic import GradingPeriodRepository
from app.repositories.assessment import DiaryAttendanceRepository, PeriodClosureRepository, PeriodResultRepository
from app.schemas.assessment import PeriodClosureOut
from app.services.assessment.errors import bad_request, conflict, not_found
from app.services.assessment.offerings import TeachingOfferingService
from app.services.assessment.snapshot import OfferingScores, period_key


class PeriodClosureService:
    """Fechamento de etapa na turma: grava media e faltas de cada aluno e bloqueia lancamentos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = PeriodClosureRepository(db)
        self.results = PeriodResultRepository(db)
        self.periods = GradingPeriodRepository(db)
        self.attendance = DiaryAttendanceRepository(db)
        self.offerings = TeachingOfferingService(db)

    def close(self, offering_id: int, period_id: int, user: Student) -> PeriodClosureOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        period = self._period_of(offering, period_id)
        if self.repo.get(offering_id, period_id):
            raise conflict("Etapa já fechada nesta turma")
        closed = self.consolidate(offering, period, user.id)
        self.repo.commit()
        return PeriodClosureOut(grading_period_id=period_id, closed_students=closed)

    def consolidate(self, offering: ClassOffering, period: GradingPeriod, closed_by_id: int | None) -> int:
        """Grava os resultados da etapa (sem commit); usado tambem no calculo final."""
        snapshot = OfferingScores(self.db, offering)
        absences = self.attendance.unjustified_absences(offering.id, period.starts_on, period.ends_on)
        existing = self.results.by_period(offering.id, period.id)
        enrollments = self.offerings.roster(offering.id)
        for enrollment in enrollments:
            result = existing.get(enrollment.id) or self.results.add(
                PeriodResult(class_offering_id=offering.id, class_enrollment_id=enrollment.id, grading_period_id=period.id)
            )
            result.average = snapshot.period_average(enrollment.id, period_key(period.id))
            result.absences = absences.get(enrollment.id, 0)
        self.repo.add(OfferingPeriodClosure(class_offering_id=offering.id, grading_period_id=period.id, closed_by_id=closed_by_id))
        return len(enrollments)

    def reopen(self, offering_id: int, period_id: int, user: Student) -> None:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        closure = self.repo.get(offering_id, period_id)
        if not closure:
            raise not_found("Etapa não está fechada nesta turma")
        for result in self.results.by_period(offering_id, period_id).values():
            self.db.delete(result)
        # O resultado final depende das etapas: volta a ficar em andamento ate novo calculo.
        for enrollment in self.offerings.roster(offering_id):
            enrollment.final_grade = None
            enrollment.result = ClassEnrollmentResult.in_progress
        self.repo.delete(closure)

    def _period_of(self, offering: ClassOffering, period_id: int) -> GradingPeriod:
        period = self.periods.get_by_id(period_id)
        if not period:
            raise not_found("Etapa de avaliação não encontrada")
        if period.term_id != offering.term_id:
            raise bad_request("A etapa não pertence ao período letivo da turma")
        return period
