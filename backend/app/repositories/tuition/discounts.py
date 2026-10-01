from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy import or_

from app.models.tuition import StudentDiscount
from app.repositories.academic._base import Repository


class StudentDiscountRepository(Repository[StudentDiscount]):
    model = StudentDiscount

    def list_by_enrollment(self, enrollment_id: UUID) -> list[StudentDiscount]:
        return (
            self.db.query(StudentDiscount)
            .filter(StudentDiscount.program_enrollment_id == enrollment_id)
            .order_by(StudentDiscount.valid_from.desc(), StudentDiscount.id.desc())
            .all()
        )

    def active_on(self, enrollment_id: UUID, day: date) -> list[StudentDiscount]:
        return (
            self.db.query(StudentDiscount)
            .filter(
                StudentDiscount.program_enrollment_id == enrollment_id,
                StudentDiscount.is_active.is_(True),
                StudentDiscount.valid_from <= day,
                or_(StudentDiscount.valid_until.is_(None), StudentDiscount.valid_until >= day),
            )
            .all()
        )
