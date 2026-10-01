from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import joinedload, selectinload

from app.models.warehouse import MaterialRequest, MaterialRequestLine, RequestStatus


class MaterialRequestRepository:
    def __init__(self, db):
        self.db = db

    def _query(self):
        return self.db.query(MaterialRequest).options(
            joinedload(MaterialRequest.requester), joinedload(MaterialRequest.class_offering),
            selectinload(MaterialRequest.lines).joinedload(MaterialRequestLine.item),
        )

    def get(self, request_id: UUID) -> MaterialRequest | None:
        return self._query().filter(MaterialRequest.id == request_id).first()

    def list(self, status: RequestStatus | None = None, requester_id: UUID | None = None) -> list[MaterialRequest]:
        query = self._query()
        if status is not None:
            query = query.filter(MaterialRequest.status == status)
        if requester_id is not None:
            query = query.filter(MaterialRequest.requester_id == requester_id)
        return query.order_by(MaterialRequest.needed_on, MaterialRequest.id).all()

    def delivered_between(self, start: date, end: date) -> list[MaterialRequest]:
        """Requisicoes retiradas no periodo (pela data de necessidade, que e a data de uso)."""
        return (
            self._query()
            .filter(MaterialRequest.status.in_((RequestStatus.delivered, RequestStatus.closed)))
            .filter(MaterialRequest.needed_on >= start, MaterialRequest.needed_on <= end)
            .all()
        )

    def delivered_for_offerings(self, offering_ids: list[UUID]) -> list[MaterialRequest]:
        if not offering_ids:
            return []
        return (
            self._query()
            .filter(MaterialRequest.class_offering_id.in_(offering_ids))
            .filter(MaterialRequest.status.in_((RequestStatus.delivered, RequestStatus.closed)))
            .all()
        )

    def add(self, request: MaterialRequest) -> MaterialRequest:
        self.db.add(request)
        return request

    def commit(self) -> None:
        self.db.commit()
