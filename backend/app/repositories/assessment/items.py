from __future__ import annotations
from uuid import UUID

from app.models.assessment import AssessmentItem
from app.repositories.academic._base import Repository


class AssessmentItemRepository(Repository[AssessmentItem]):
    model = AssessmentItem

    def list_by_offering(self, offering_id: UUID) -> list[AssessmentItem]:
        return (
            self.db.query(AssessmentItem)
            .filter(AssessmentItem.class_offering_id == offering_id)
            .order_by(AssessmentItem.grading_period_id, AssessmentItem.id)
            .all()
        )
