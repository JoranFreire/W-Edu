from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.warehouse import MaterialRequest, MaterialRequestLine, RequestStatus
from app.policies.offering_access import ensure_can_teach
from app.repositories.schedule import ClassOfferingRepository
from app.repositories.warehouse import MaterialRequestRepository, WarehouseItemRepository
from app.schemas.warehouse import RequestCreate, RequestOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.warehouse.views import request_out


class MaterialRequestService:
    """Lado de quem pede: abre requisicao (com turma opcional), acompanha e cancela enquanto pendente."""

    def __init__(self, db: Session):
        self.repo = MaterialRequestRepository(db)
        self.items = WarehouseItemRepository(db)
        self.offerings = ClassOfferingRepository(db)

    def create(self, requester: Student, data: RequestCreate) -> RequestOut:
        if data.class_offering_id is not None:
            offering = self.offerings.get_by_id(data.class_offering_id)
            if not offering:
                raise not_found("Turma não encontrada")
            ensure_can_teach(requester, offering)
        item_ids = [line.item_id for line in data.lines]
        if len(set(item_ids)) != len(item_ids):
            raise bad_request("Material repetido na requisição")
        for item_id in item_ids:
            item = self.items.get_by_id(item_id)
            if not item or not item.is_active:
                raise not_found("Material não encontrado")
        request = self.repo.add(MaterialRequest(
            requester_id=requester.id, class_offering_id=data.class_offering_id, purpose=data.purpose, needed_on=data.needed_on,
            lines=[MaterialRequestLine(item_id=line.item_id, quantity_requested=line.quantity) for line in data.lines],
        ))
        self.repo.commit()
        return request_out(self.repo.get(request.id))

    def list_mine(self, requester: Student) -> list[RequestOut]:
        return [request_out(r) for r in sorted(self.repo.list(requester_id=requester.id), key=lambda r: r.id, reverse=True)]

    def cancel(self, requester: Student, request_id: int) -> RequestOut:
        request = self.repo.get(request_id)
        if not request or request.requester_id != requester.id:
            raise not_found("Requisição não encontrada")
        if request.status not in (RequestStatus.pending, RequestStatus.approved):
            raise conflict("Só requisições pendentes ou aprovadas e não retiradas podem ser canceladas")
        request.status = RequestStatus.cancelled
        self.repo.commit()
        return request_out(request)
