from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.schedule import ClassEnrollmentResult
from app.models.student import Student
from app.policies.assessment_locks import is_offering_finalized
from app.repositories.assessment import PeriodResultRepository, StudentEnrollmentRepository
from app.schemas.assessment import ReportCardEntry, ReportCardPeriod
from app.services.assessment.schemes import GradingSchemeService


class ReportCardService:
    """Boletim do aluno: etapas fechadas e, depois da finalizacao, o resultado final."""

    def __init__(self, db: Session):
        self.enrollments = StudentEnrollmentRepository(db)
        self.results = PeriodResultRepository(db)
        self.schemes = GradingSchemeService(db)

    def for_student(self, student: Student) -> list[ReportCardEntry]:
        enrollments = self.enrollments.for_student(student.id)
        results: dict[int, list] = {}
        for result in self.results.by_enrollments([e.id for e in enrollments]):
            results.setdefault(result.class_enrollment_id, []).append(result)
        cards = []
        for enrollment in enrollments:
            offering = enrollment.class_offering
            periods = sorted(results.get(enrollment.id, []), key=lambda r: r.grading_period.order)
            if not periods and not is_offering_finalized(offering):
                continue
            finalized = is_offering_finalized(offering)
            scheme = self.schemes.effective_for(offering)
            cards.append(ReportCardEntry(
                class_offering_id=offering.id,
                offering_name=offering.name,
                periods=[ReportCardPeriod(name=r.grading_period.name, average=r.average, absences=r.absences) for r in periods],
                final_grade=enrollment.final_grade if finalized else None,
                recovery_score=enrollment.recovery_score if finalized else None,
                attendance_rate=enrollment.attendance_rate if finalized else None,
                result=enrollment.result if finalized else ClassEnrollmentResult.in_progress,
                finalized=finalized,
                passing_grade=scheme.passing_grade,
                min_attendance=scheme.min_attendance,
            ))
        return cards
