"""Almoxarifado: materiais (de consumo ou permanentes), entradas e requisicoes dos professores."""

from uuid import UUID

from datetime import date, datetime, timezone
import enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MaterialKind(str, enum.Enum):
    consumable = "consumable"  # gasto no uso (papel, tinta)
    durable = "durable"        # emprestado e devolvido (jogos, bolas)


class EntryOrigin(str, enum.Enum):
    purchase = "purchase"
    donation = "donation"


class RequestStatus(str, enum.Enum):
    pending = "pending"        # aguardando aprovacao
    approved = "approved"      # aprovada (total ou parcial), aguardando retirada
    rejected = "rejected"
    delivered = "delivered"    # retirada; materiais permanentes aguardando devolucao
    closed = "closed"          # tudo entregue e devolvido (ou baixado)
    cancelled = "cancelled"


class WarehouseItem(TenantMixin, Base):
    __tablename__ = "warehouse_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(80))
    kind: Mapped[MaterialKind] = mapped_column(SAEnum(MaterialKind), default=MaterialKind.consumable)
    unit: Mapped[str] = mapped_column(String(40), default="unidade")
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    location: Mapped[str | None] = mapped_column(String(120))
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WarehouseEntry(TenantMixin, Base):
    """Entrada de material (compra ou doacao), com custo e financiador."""

    __tablename__ = "warehouse_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse_items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    origin: Mapped[EntryOrigin] = mapped_column(SAEnum(EntryOrigin), default=EntryOrigin.purchase)
    funding_source_id: Mapped[UUID | None] = mapped_column(ForeignKey("funding_sources.id"), index=True)
    received_on: Mapped[date] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    item: Mapped["WarehouseItem"] = relationship()


class MaterialRequest(TenantMixin, Base):
    """Requisicao do professor: sempre passa por aprovacao antes da retirada."""

    __tablename__ = "material_requests"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    requester_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    class_offering_id: Mapped[UUID | None] = mapped_column(ForeignKey("class_offerings.id"), index=True)
    purpose: Mapped[str] = mapped_column(Text)
    needed_on: Mapped[date] = mapped_column(Date)
    status: Mapped[RequestStatus] = mapped_column(SAEnum(RequestStatus), default=RequestStatus.pending)
    decision_note: Mapped[str | None] = mapped_column(Text)
    decided_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    return_due_on: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    requester: Mapped["Student"] = relationship(foreign_keys=[requester_id])
    class_offering: Mapped["ClassOffering | None"] = relationship()
    lines: Mapped[list["MaterialRequestLine"]] = relationship(
        back_populates="request", cascade="all, delete-orphan", order_by="MaterialRequestLine.id"
    )


class MaterialRequestLine(TenantMixin, Base):
    __tablename__ = "material_request_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    request_id: Mapped[UUID] = mapped_column(ForeignKey("material_requests.id", ondelete="CASCADE"), index=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse_items.id"), index=True)
    quantity_requested: Mapped[int] = mapped_column(Integer)
    quantity_approved: Mapped[int | None] = mapped_column(Integer)
    quantity_delivered: Mapped[int] = mapped_column(Integer, default=0)
    quantity_returned: Mapped[int] = mapped_column(Integer, default=0)
    quantity_lost: Mapped[int] = mapped_column(Integer, default=0)   # avaria ou perda na devolucao
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)  # congelado na retirada

    request: Mapped["MaterialRequest"] = relationship(back_populates="lines")
    item: Mapped["WarehouseItem"] = relationship()
