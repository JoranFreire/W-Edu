from __future__ import annotations
from uuid import UUID

from app.models.tuition import TuitionPlan
from app.repositories.academic._base import Repository


class TuitionPlanRepository(Repository[TuitionPlan]):
    model = TuitionPlan

    def list(self, term_id: UUID | None = None) -> list[TuitionPlan]:
        query = self.db.query(TuitionPlan)
        if term_id is not None:
            query = query.filter(TuitionPlan.term_id == term_id)
        return query.order_by(TuitionPlan.first_due_on.desc(), TuitionPlan.id.desc()).all()
