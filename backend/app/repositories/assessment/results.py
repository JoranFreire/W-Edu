from __future__ import annotations

from app.models.assessment import OfferingPeriodClosure, PeriodResult
from app.models.schedule import ClassEnrollment, ClassOffering
from app.repositories.academic._base import Repository


class PeriodClosureRepository(Repository[OfferingPeriodClosure]):
    model = OfferingPeriodClosure

    def closed_period_ids(self, offering_id: int) -> set[int]:
        rows = self.db.query(OfferingPeriodClosure.grading_period_id).filter(OfferingPeriodClosure.class_offering_id == offering_id).all()
        return {row[0] for row in rows}

    def get(self, offering_id: int, period_id: int) -> OfferingPeriodClosure | None:
        return (
            self.db.query(OfferingPeriodClosure)
            .filter(OfferingPeriodClosure.class_offering_id == offering_id, OfferingPeriodClosure.grading_period_id == period_id)
            .first()
        )


class PeriodResultRepository(Repository[PeriodResult]):
    model = PeriodResult

    def by_offering(self, offering_id: int) -> list[PeriodResult]:
        return self.db.query(PeriodResult).filter(PeriodResult.class_offering_id == offering_id).all()

    def by_period(self, offering_id: int, period_id: int) -> dict[int, PeriodResult]:
        rows = (
            self.db.query(PeriodResult)
            .filter(PeriodResult.class_offering_id == offering_id, PeriodResult.grading_period_id == period_id)
            .all()
        )
        return {row.class_enrollment_id: row for row in rows}

    def by_enrollments(self, enrollment_ids: list[int]) -> list[PeriodResult]:
        if not enrollment_ids:
            return []
        return self.db.query(PeriodResult).filter(PeriodResult.class_enrollment_id.in_(enrollment_ids)).all()


class StudentEnrollmentRepository(Repository[ClassEnrollment]):
    """Inscricoes do proprio aluno, para o boletim."""

    model = ClassEnrollment

    def for_student(self, student_id: int) -> list[ClassEnrollment]:
        return (
            self.db.query(ClassEnrollment)
            .join(ClassOffering, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(ClassEnrollment.student_id == student_id)
            .order_by(ClassOffering.starts_at.desc())
            .all()
        )
