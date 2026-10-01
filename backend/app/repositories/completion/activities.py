from __future__ import annotations
from uuid import UUID

from sqlalchemy import func

from app.models.academic_groups import ProgramEnrollment
from app.models.completion import ComplementaryActivity, ReviewStatus
from app.repositories.academic._base import Repository


class ComplementaryActivityRepository(Repository[ComplementaryActivity]):
    model = ComplementaryActivity

    def list_by_enrollment(self, enrollment_id: UUID) -> list[ComplementaryActivity]:
        return (
            self.db.query(ComplementaryActivity)
            .filter(ComplementaryActivity.program_enrollment_id == enrollment_id)
            .order_by(ComplementaryActivity.occurred_on.desc(), ComplementaryActivity.id.desc())
            .all()
        )

    def list_by_student(self, student_id: UUID) -> list[ComplementaryActivity]:
        return (
            self.db.query(ComplementaryActivity)
            .join(ProgramEnrollment, ProgramEnrollment.id == ComplementaryActivity.program_enrollment_id)
            .filter(ProgramEnrollment.student_id == student_id)
            .order_by(ComplementaryActivity.occurred_on.desc(), ComplementaryActivity.id.desc())
            .all()
        )

    def approved_hours(self, enrollment_id: UUID) -> int:
        total = (
            self.db.query(func.sum(ComplementaryActivity.hours_approved))
            .filter(ComplementaryActivity.program_enrollment_id == enrollment_id, ComplementaryActivity.status == ReviewStatus.approved)
            .scalar()
        )
        return int(total or 0)
