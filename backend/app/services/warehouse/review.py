from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import NotificationEventType
from app.models.student import Student
from app.models.warehouse import MaterialKind, MaterialRequest, RequestStatus
from app.core.signing import validation_code
from app.repositories.warehouse import MaterialRequestRepository, WarehouseItemRepository
from app.schemas.warehouse import ApprovalInput, RejectInput, RequestOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.notifications.events import NotificationEventService
from app.services.warehouse.catalog import WarehouseCatalogService
from app.services.warehouse.views import request_out

STATUS_LABELS = {RequestStatus.approved: "aprovada", RequestStatus.rejected: "recusada"}


class MaterialRequestReviewService:
    """Aprovacao (total ou parcial, por linha) ou recusa da requisicao, com aviso a quem pediu."""

    def __init__(self, db: Session):
        self.repo = MaterialRequestRepository(db)
        self.notices = NotificationEventService(db)
        self.items = WarehouseItemRepository(db)
        self.catalog = WarehouseCatalogService(db)

    def list(self, status: RequestStatus | None) -> list[RequestOut]:
        return [request_out(r) for r in self.repo.list(status=status)]

    def approve(self, request_id: UUID, data: ApprovalInput, reviewer: Student) -> RequestOut:
        request = self._pending(request_id)
        by_id = {line.id: line for line in request.lines}
        decided = {approval.line_id: approval.quantity for approval in data.lines}
        if set(decided) != set(by_id):
            raise bad_request("Informe a quantidade aprovada de todas as linhas")
        for line_id, quantity in decided.items():
            if quantity > by_id[line_id].quantity_requested:
                raise bad_request(f"{by_id[line_id].item.name}: aprovado acima do pedido")
            by_id[line_id].quantity_approved = quantity
        if not any(decided.values()):
            return self._close(request, RequestStatus.rejected, data.note or "Nenhum material aprovado", reviewer)
        self._ensure_free({by_id[line_id].item_id: quantity for line_id, quantity in decided.items() if quantity}, request)
        has_durable = any(by_id[i].item.kind == MaterialKind.durable and q for i, q in decided.items())
        request.return_due_on = (data.return_due_on or request.needed_on) if has_durable else None
        request.pickup_code = validation_code()
        return self._close(request, RequestStatus.approved, data.note, reviewer)

    def _ensure_free(self, wanted: dict[UUID, int], request: MaterialRequest) -> None:
        """Aprovar reserva: nao se aprova o que o saldo (menos as outras aprovacoes) nao cobre."""
        locked = self.items.lock_many(list(wanted))
        free = self.catalog.free_for_approval(list(wanted), excluding_request_id=request.id)
        short = [f"{locked[item_id].name} ({free[item_id]} livre(s))" for item_id, quantity in wanted.items() if quantity > free[item_id]]
        if short:
            raise conflict("Saldo insuficiente para aprovar: " + ", ".join(short))

    def reject(self, request_id: UUID, data: RejectInput, reviewer: Student) -> RequestOut:
        request = self._pending(request_id)
        for line in request.lines:
            line.quantity_approved = 0
        return self._close(request, RequestStatus.rejected, data.note, reviewer)

    def _close(self, request: MaterialRequest, status: RequestStatus, note: str | None, reviewer: Student) -> RequestOut:
        request.status, request.decision_note = status, note
        request.decided_by_id, request.decided_at = reviewer.id, datetime.now(timezone.utc)
        self.repo.commit()
        hint = " Mostre o QR da requisição na retirada." if status == RequestStatus.approved else ""
        self.notices.publish(
            NotificationEventType.material_request_decided,
            {"status_label": STATUS_LABELS[status], "needed_on": request.needed_on.strftime("%d/%m/%Y"), "purpose": request.purpose[:80],
             "note": (f" Observação: {note}" if note else "") + hint},
            recipient_student_id=request.requester_id,
        )
        return request_out(request)

    def _pending(self, request_id: UUID) -> MaterialRequest:
        request = self.repo.get(request_id)
        if not request:
            raise not_found("Requisição não encontrada")
        if request.status != RequestStatus.pending:
            raise conflict("Requisição já analisada")
        return request
