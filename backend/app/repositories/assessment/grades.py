from __future__ import annotations

from sqlalchemy import func

from app.models.assessment import AssessmentItem, GradeEntry
from app.models.quiz import QuizAttempt
from app.repositories.academic._base import Repository


class GradeEntryRepository(Repository[GradeEntry]):
    model = GradeEntry

    def by_item(self, item_id: int) -> dict[int, GradeEntry]:
        entries = self.db.query(GradeEntry).filter(GradeEntry.assessment_item_id == item_id).all()
        return {entry.class_enrollment_id: entry for entry in entries}

    def by_offering(self, offering_id: int) -> list[GradeEntry]:
        return (
            self.db.query(GradeEntry)
            .join(AssessmentItem, GradeEntry.assessment_item_id == AssessmentItem.id)
            .filter(AssessmentItem.class_offering_id == offering_id)
            .all()
        )

    def best_quiz_scores(self, quiz_id: int, student_ids: list[int]) -> dict[int, int]:
        """Melhor tentativa (0-100) de cada aluno no quiz."""
        if not student_ids:
            return {}
        rows = (
            self.db.query(QuizAttempt.student_id, func.max(QuizAttempt.score))
            .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id.in_(student_ids))
            .group_by(QuizAttempt.student_id)
            .all()
        )
        return dict(rows)
