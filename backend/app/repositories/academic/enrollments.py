from __future__ import annotations

from sqlalchemy.orm import joinedload

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.repositories.academic._base import Repository

OPEN_STATUSES = (ProgramEnrollmentStatus.active, ProgramEnrollmentStatus.locked)


class ProgramEnrollmentRepository(Repository[ProgramEnrollment]):
    model = ProgramEnrollment

    def _query(self):
        return self.db.query(ProgramEnrollment).options(
            joinedload(ProgramEnrollment.student), joinedload(ProgramEnrollment.program)
        )

    def list(
        self,
        program_id: int | None = None,
        status: ProgramEnrollmentStatus | None = None,
        student_id: int | None = None,
    ) -> list[ProgramEnrollment]:
        query = self._query()
        if program_id is not None:
            query = query.filter(ProgramEnrollment.program_id == program_id)
        if status is not None:
            query = query.filter(ProgramEnrollment.status == status)
        if student_id is not None:
            query = query.filter(ProgramEnrollment.student_id == student_id)
        return query.order_by(ProgramEnrollment.registration_number).all()

    def get_open(self, student_id: int, program_id: int) -> ProgramEnrollment | None:
        return (
            self.db.query(ProgramEnrollment)
            .filter(
                ProgramEnrollment.student_id == student_id,
                ProgramEnrollment.program_id == program_id,
                ProgramEnrollment.status.in_(OPEN_STATUSES),
            )
            .first()
        )

    def registration_exists(self, number: str) -> bool:
        return self.db.query(ProgramEnrollment.id).filter(ProgramEnrollment.registration_number == number).first() is not None

    def count_with_prefix(self, prefix: str) -> int:
        return self.db.query(ProgramEnrollment.id).filter(ProgramEnrollment.registration_number.like(f"{prefix}%")).count()
