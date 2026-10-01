from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_calendar import GradingPeriodStatus, TermStatus
from app.models.schedule import ClassEnrollment, ClassEnrollmentResult, ClassEnrollmentStatus, ClassOffering, ClassStatus
from app.models.student import Student
from app.policies.assessment_locks import ensure_offering_open, is_offering_finalized
from app.repositories.academic import GradingPeriodRepository
from app.repositories.assessment import ClassDiaryRepository, DiaryAttendanceRepository, PeriodClosureRepository, PeriodResultRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import FinalResultRow, OfferingResultsOut, PeriodResultOut, RecoveryInput
from app.services.assessment.attendance_rate import attendance_rate
from app.services.assessment.averages import mean_of
from app.services.assessment.closures import PeriodClosureService
from app.services.assessment.errors import bad_request, conflict
from app.services.assessment.offerings import TeachingOfferingService
from app.services.assessment.result_notices import ResultNoticeService
from app.services.assessment.result_rules import decide
from app.services.assessment.snapshot import NO_PERIOD, OfferingScores

RECOVERABLE = {ClassEnrollmentResult.recovery, ClassEnrollmentResult.failed}
UNFINISHED = {ClassEnrollmentResult.in_progress, ClassEnrollmentResult.recovery}


class FinalResultService:
    """Resultado final da turma: media das etapas fechadas, frequencia, recuperacao e finalizacao."""

    def __init__(self, db: Session):
        self.db = db
        self.offerings = TeachingOfferingService(db)
        self.closures = PeriodClosureService(db)
        self.closure_repo = PeriodClosureRepository(db)
        self.results = PeriodResultRepository(db)
        self.periods = GradingPeriodRepository(db)
        self.diary = ClassDiaryRepository(db)
        self.attendance = DiaryAttendanceRepository(db)
        self.notices = ResultNoticeService(db)

    def overview(self, offering_id: int, user: Student) -> OfferingResultsOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        snapshot = OfferingScores(self.db, offering)
        closed = self.closure_repo.closed_period_ids(offering_id)
        by_enrollment: dict[int, list] = {}
        for result in self.results.by_offering(offering_id):
            by_enrollment.setdefault(result.class_enrollment_id, []).append(result)
        rows = [
            FinalResultRow(
                class_enrollment_id=e.id,
                student=PersonSummary.model_validate(e.student),
                periods=[PeriodResultOut(grading_period_id=r.grading_period_id, average=r.average, absences=r.absences)
                         for r in sorted(by_enrollment.get(e.id, []), key=lambda r: r.grading_period.order)],
                average=self._average(snapshot, e.id, by_enrollment.get(e.id, [])),
                recovery_score=e.recovery_score,
                final_grade=e.final_grade,
                attendance_rate=e.attendance_rate,
                result=e.result,
            )
            for e in self.offerings.roster(offering_id)
        ]
        return OfferingResultsOut(
            scheme=snapshot.scheme,
            closed_period_ids=sorted(closed),
            pending_period_ids=self._pending_periods(snapshot, closed),
            finalized=is_offering_finalized(offering),
            rows=rows,
        )

    def compute(self, offering_id: int, user: Student) -> OfferingResultsOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        self._consolidate_pending(offering, user)
        self._apply(offering)
        self.db.commit()
        return self.overview(offering_id, user)

    def save_recovery(self, offering_id: int, values: list[RecoveryInput], user: Student) -> OfferingResultsOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        scheme = OfferingScores(self.db, offering).scheme
        if not scheme.recovery_enabled:
            raise bad_request("O esquema da turma não prevê recuperação")
        enrollments = {e.id: e for e in self.offerings.roster(offering_id)}
        for value in values:
            enrollment = enrollments.get(value.class_enrollment_id)
            if enrollment is None:
                raise bad_request("Aluno não pertence à turma")
            if enrollment.result not in RECOVERABLE:
                raise bad_request(f"{enrollment.student.name} não está em recuperação")
            if value.score is not None and value.score > scheme.max_value:
                raise bad_request(f"Nota acima do máximo ({scheme.max_value:g})")
            enrollment.recovery_score = value.score
        self._apply(offering)
        self.db.commit()
        return self.overview(offering_id, user)

    def finalize(self, offering_id: int, user: Student) -> OfferingResultsOut:
        """Publica o resultado: turma e inscricoes concluidas, lancamentos bloqueados e aviso ao aluno."""
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        self._consolidate_pending(offering, user)
        enrollments = self._apply(offering)
        if pending := [e.student.name for e in enrollments if e.result in UNFINISHED]:
            raise conflict(f"Resultado pendente para: {', '.join(pending)}")
        offering.status = ClassStatus.completed
        for enrollment in enrollments:
            enrollment.status = ClassEnrollmentStatus.completed
        self.db.commit()
        self.notices.published(offering, enrollments)
        return self.overview(offering_id, user)

    def _apply(self, offering: ClassOffering) -> list[ClassEnrollment]:
        snapshot = OfferingScores(self.db, offering)
        total_lessons = self.diary.total_lessons(offering.id)
        absences = self.attendance.unjustified_absences(offering.id)
        by_enrollment: dict[int, list] = {}
        for result in self.results.by_offering(offering.id):
            by_enrollment.setdefault(result.class_enrollment_id, []).append(result)
        enrollments = self.offerings.roster(offering.id)
        for enrollment in enrollments:
            rate = attendance_rate(total_lessons, absences.get(enrollment.id, 0))
            outcome = decide(self._average(snapshot, enrollment.id, by_enrollment.get(enrollment.id, [])), enrollment.recovery_score, rate, snapshot.scheme)
            enrollment.final_grade, enrollment.result, enrollment.attendance_rate = outcome.final_grade, outcome.result, rate
        return enrollments

    @staticmethod
    def _average(snapshot: OfferingScores, enrollment_id: int, period_results: list) -> float | None:
        """Media das etapas consolidadas, mais avaliacoes sem etapa (calculadas na hora)."""
        values = [result.average for result in period_results]
        if NO_PERIOD in snapshot.items_by_period:
            values.append(snapshot.period_average(enrollment_id, NO_PERIOD))
        return mean_of(values)

    @staticmethod
    def _pending_periods(snapshot: OfferingScores, closed: set[int]) -> list[int]:
        return sorted(int(key) for key in snapshot.items_by_period if key != NO_PERIOD and int(key) not in closed)

    def _consolidate_pending(self, offering: ClassOffering, user: Student) -> None:
        """Etapas com avaliacoes precisam estar fechadas; as encerradas na instituicao sao consolidadas aqui."""
        pending = self._pending_periods(OfferingScores(self.db, offering), self.closure_repo.closed_period_ids(offering.id))
        open_names = []
        for period_id in pending:
            period = self.periods.get_by_id(period_id)
            if period.status == GradingPeriodStatus.closed or period.term.status == TermStatus.closed:
                self.closures.consolidate(offering, period, user.id)
            else:
                open_names.append(period.name)
        if open_names:
            raise conflict(f"Feche as etapas antes do resultado: {', '.join(open_names)}")
        self.db.flush()
