from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.academic import GradingPeriodRepository
from app.repositories.assessment import ClassDiaryRepository, DiaryAttendanceRepository, PeriodClosureRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import AssessmentItemOut, GradebookOut, GradebookPeriod, GradebookRow
from app.services.assessment.attendance_rate import attendance_rate
from app.services.assessment.averages import concept_for, mean_of
from app.services.assessment.offerings import TeachingOfferingService
from app.services.assessment.snapshot import NO_PERIOD, OfferingScores


class GradebookService:
    """Boletim parcial da turma: notas por avaliacao, media por etapa, media geral e frequencia."""

    def __init__(self, db: Session):
        self.db = db
        self.offerings = TeachingOfferingService(db)
        self.periods = GradingPeriodRepository(db)
        self.closures = PeriodClosureRepository(db)
        self.diary = ClassDiaryRepository(db)
        self.attendance = DiaryAttendanceRepository(db)

    def build(self, offering_id: UUID, user: Student) -> GradebookOut:
        offering = self.offerings.get_for_teaching(offering_id, user)
        snapshot = OfferingScores(self.db, offering)
        scheme, items = snapshot.scheme, snapshot.items
        periods = self.periods.list_by_term(offering.term_id) if offering.term_id else []
        closed = self.closures.closed_period_ids(offering_id)
        total_lessons = self.diary.total_lessons(offering_id)
        absences = self.attendance.unjustified_absences(offering_id)

        period_keys = [str(p.id) for p in periods if str(p.id) in snapshot.items_by_period]
        if NO_PERIOD in snapshot.items_by_period:
            period_keys.append(NO_PERIOD)

        rows = []
        for enrollment in self.offerings.roster(offering_id):
            period_averages = {key: snapshot.period_average(enrollment.id, key) for key in period_keys}
            overall = mean_of(period_averages.values())
            student_absences = absences.get(enrollment.id, 0)
            rows.append(GradebookRow(
                class_enrollment_id=enrollment.id,
                student=PersonSummary.model_validate(enrollment.student),
                scores={str(i.id): snapshot.score(i.id, enrollment.id) for i in items},
                period_averages=period_averages,
                average=overall,
                concept=concept_for(overall, [band.model_dump() for band in scheme.concepts]),
                absences=student_absences,
                attendance_rate=attendance_rate(total_lessons, student_absences),
            ))

        headers = [
            GradebookPeriod(id=p.id, name=p.name, status="closed" if p.id in closed else p.status.value)
            for p in periods
            if str(p.id) in period_keys
        ]
        if NO_PERIOD in period_keys:
            headers.append(GradebookPeriod(id=None, name="Sem etapa", status="open"))
        return GradebookOut(
            scheme=scheme,
            periods=headers,
            items=[AssessmentItemOut.model_validate(item) for item in items],
            rows=rows,
            total_lessons=total_lessons,
        )
