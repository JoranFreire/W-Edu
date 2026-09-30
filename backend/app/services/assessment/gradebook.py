from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.academic import GradingPeriodRepository
from app.repositories.assessment import AssessmentItemRepository, ClassDiaryRepository, DiaryAttendanceRepository, GradeEntryRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import AssessmentItemOut, GradebookOut, GradebookPeriod, GradebookRow
from app.services.assessment.attendance_rate import attendance_rate
from app.services.assessment.averages import ScoredItem, average, concept_for, mean_of
from app.services.assessment.offerings import TeachingOfferingService
from app.services.assessment.schemes import GradingSchemeService

NO_PERIOD = "none"


class GradebookService:
    """Boletim parcial da turma: notas por avaliacao, media por etapa, media geral e frequencia."""

    def __init__(self, db: Session):
        self.offerings = TeachingOfferingService(db)
        self.schemes = GradingSchemeService(db)
        self.items = AssessmentItemRepository(db)
        self.grades = GradeEntryRepository(db)
        self.periods = GradingPeriodRepository(db)
        self.diary = ClassDiaryRepository(db)
        self.attendance = DiaryAttendanceRepository(db)

    def build(self, offering_id: int, user: Student) -> GradebookOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        scheme = self.schemes.effective_for(offering)
        items = self.items.list_by_offering(offering_id)
        periods = self.periods.list_by_term(offering.term_id) if offering.term_id else []
        scores = {(g.assessment_item_id, g.class_enrollment_id): g.score for g in self.grades.by_offering(offering_id)}
        total_lessons = self.diary.total_lessons(offering_id)
        absences = self.attendance.unjustified_absences(offering_id)

        items_by_period: dict[str, list] = defaultdict(list)
        for item in items:
            items_by_period[str(item.grading_period_id) if item.grading_period_id else NO_PERIOD].append(item)
        period_keys = [str(p.id) for p in periods if str(p.id) in items_by_period]
        if NO_PERIOD in items_by_period:
            period_keys.append(NO_PERIOD)

        rows = []
        for enrollment in self.offerings.active_enrollments(offering_id):
            period_averages = {
                key: average(
                    [ScoredItem(scores.get((i.id, enrollment.id)), i.max_score, i.weight) for i in items_by_period[key]],
                    scheme.formula, scheme.min_value, scheme.max_value,
                )
                for key in period_keys
            }
            overall = mean_of(period_averages.values())
            student_absences = absences.get(enrollment.id, 0)
            rows.append(GradebookRow(
                class_enrollment_id=enrollment.id,
                student=PersonSummary.model_validate(enrollment.student),
                scores={str(i.id): scores.get((i.id, enrollment.id)) for i in items},
                period_averages=period_averages,
                average=overall,
                concept=concept_for(overall, [band.model_dump() for band in scheme.concepts]),
                absences=student_absences,
                attendance_rate=attendance_rate(total_lessons, student_absences),
            ))

        headers = [GradebookPeriod(id=p.id, name=p.name, status=p.status.value) for p in periods if str(p.id) in period_keys]
        if NO_PERIOD in period_keys:
            headers.append(GradebookPeriod(id=None, name="Sem etapa", status="open"))
        return GradebookOut(
            scheme=scheme,
            periods=headers,
            items=[AssessmentItemOut.model_validate(item) for item in items],
            rows=rows,
            total_lessons=total_lessons,
        )
