from __future__ import annotations

from datetime import date

from app.models.school_life import AgendaItem
from app.repositories.academic._base import Repository


class AgendaRepository(Repository[AgendaItem]):
    model = AgendaItem

    def list_by_groups(self, group_ids: list[int], from_date: date | None = None) -> list[AgendaItem]:
        if not group_ids:
            return []
        query = self.db.query(AgendaItem).filter(AgendaItem.class_group_id.in_(group_ids))
        if from_date is not None:
            query = query.filter(AgendaItem.due_on >= from_date)
        return query.order_by(AgendaItem.due_on, AgendaItem.id).all()
