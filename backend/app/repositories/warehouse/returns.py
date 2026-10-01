from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import joinedload

from app.models.warehouse import MaterialRequest, MaterialReturn
from app.repositories.academic._base import Repository


class MaterialReturnRepository(Repository[MaterialReturn]):
    model = MaterialReturn

    def list_by_item(self, item_id: UUID) -> list[MaterialReturn]:
        return (
            self.db.query(MaterialReturn)
            .options(joinedload(MaterialReturn.received_by), joinedload(MaterialReturn.request).joinedload(MaterialRequest.requester))
            .filter(MaterialReturn.item_id == item_id)
            .all()
        )
