from __future__ import annotations
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models.social_programs import BenefitDelivery, BenefitItem, BenefitStockEntry
from app.repositories.academic._base import Repository


class BenefitItemRepository(Repository[BenefitItem]):
    model = BenefitItem

    def list(self) -> list[BenefitItem]:
        return self.db.query(BenefitItem).order_by(BenefitItem.is_active.desc(), BenefitItem.name).all()

    def balances(self, item_ids: list[UUID]) -> dict[UUID, int]:
        """Saldo em estoque: entradas menos entregas."""
        if not item_ids:
            return {}
        received = dict(
            self.db.query(BenefitStockEntry.item_id, func.sum(BenefitStockEntry.quantity))
            .filter(BenefitStockEntry.item_id.in_(item_ids)).group_by(BenefitStockEntry.item_id).all()
        )
        delivered = dict(
            self.db.query(BenefitDelivery.item_id, func.sum(BenefitDelivery.quantity))
            .filter(BenefitDelivery.item_id.in_(item_ids)).group_by(BenefitDelivery.item_id).all()
        )
        return {item_id: int(received.get(item_id) or 0) - int(delivered.get(item_id) or 0) for item_id in item_ids}

    def lock(self, item_id: UUID) -> BenefitItem | None:
        """Trava o item durante a entrega (duas entregas disputando o mesmo estoque)."""
        return self.db.query(BenefitItem).filter(BenefitItem.id == item_id).with_for_update().first()


class BenefitStockRepository(Repository[BenefitStockEntry]):
    model = BenefitStockEntry

    def list_by_item(self, item_id: UUID) -> list[BenefitStockEntry]:
        return (
            self.db.query(BenefitStockEntry)
            .filter(BenefitStockEntry.item_id == item_id)
            .order_by(BenefitStockEntry.received_on.desc(), BenefitStockEntry.id.desc())
            .all()
        )

    def received_cost(self, funding_id: UUID) -> int:
        total = (
            self.db.query(func.sum(BenefitStockEntry.quantity * BenefitStockEntry.unit_cost_cents))
            .filter(BenefitStockEntry.funding_source_id == funding_id)
            .scalar()
        )
        return int(total or 0)


class BenefitDeliveryRepository(Repository[BenefitDelivery]):
    model = BenefitDelivery

    def list_by_offering(self, offering_id: UUID) -> list[BenefitDelivery]:
        return (
            self.db.query(BenefitDelivery)
            .options(joinedload(BenefitDelivery.item), joinedload(BenefitDelivery.student))
            .filter(BenefitDelivery.class_offering_id == offering_id)
            .order_by(BenefitDelivery.delivered_on.desc(), BenefitDelivery.id.desc())
            .all()
        )

    def list_by_student(self, student_id: UUID) -> list[BenefitDelivery]:
        return (
            self.db.query(BenefitDelivery)
            .options(joinedload(BenefitDelivery.item), joinedload(BenefitDelivery.student))
            .filter(BenefitDelivery.student_id == student_id)
            .order_by(BenefitDelivery.delivered_on.desc(), BenefitDelivery.id.desc())
            .all()
        )

    def delivered_in_meeting(self, meeting_id: UUID, item_id: UUID) -> set[UUID]:
        rows = (
            self.db.query(BenefitDelivery.student_id)
            .filter(BenefitDelivery.scheduled_meeting_id == meeting_id, BenefitDelivery.item_id == item_id)
            .all()
        )
        return {row[0] for row in rows}

    def usage(self, offering_ids: list[UUID]) -> list[tuple[str, str, int, int]]:
        """(item, unidade, quantidade, custo) entregues nas turmas."""
        if not offering_ids:
            return []
        rows = (
            self.db.query(
                BenefitItem.name, BenefitItem.unit, func.sum(BenefitDelivery.quantity),
                func.sum(BenefitDelivery.quantity * BenefitDelivery.unit_cost_cents),
            )
            .join(BenefitItem, BenefitItem.id == BenefitDelivery.item_id)
            .filter(BenefitDelivery.class_offering_id.in_(offering_ids))
            .group_by(BenefitItem.name, BenefitItem.unit)
            .order_by(BenefitItem.name)
            .all()
        )
        return [(name, unit, int(quantity or 0), int(cost or 0)) for name, unit, quantity, cost in rows]
