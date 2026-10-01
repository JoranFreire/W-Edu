from __future__ import annotations
from uuid import UUID

from app.models.school_life import StudentOccurrence
from app.repositories.academic._base import Repository


class OccurrenceRepository(Repository[StudentOccurrence]):
    model = StudentOccurrence

    def list_by_student(self, student_id: UUID) -> list[StudentOccurrence]:
        return (
            self.db.query(StudentOccurrence)
            .filter(StudentOccurrence.student_id == student_id)
            .order_by(StudentOccurrence.occurred_on.desc(), StudentOccurrence.id.desc())
            .all()
        )
