"""Programas sociais: financiadores das turmas e beneficios entregues aos alunos (lanche, material, transporte...)."""

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


class FundingKind(str, enum.Enum):
    agreement = "agreement"          # convenio
    government = "government"        # prefeitura, estado ou uniao
    system_s = "system_s"            # Sistema S (gratuidade)
    parliamentary = "parliamentary"  # emenda parlamentar
    donation = "donation"
    own = "own"                      # recursos proprios
    other = "other"


class BenefitKind(str, enum.Enum):
    snack = "snack"          # lanche
    material = "material"    # kit ou material didatico
    uniform = "uniform"
    transport = "transport"  # vale-transporte
    stipend = "stipend"      # auxilio em dinheiro
    other = "other"


class StockOrigin(str, enum.Enum):
    purchase = "purchase"
    donation = "donation"


class FundingSource(TenantMixin, Base):
    """Fonte de recursos que financia turmas e beneficios; base da prestacao de contas."""

    __tablename__ = "funding_sources"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[FundingKind] = mapped_column(SAEnum(FundingKind), default=FundingKind.agreement)
    agreement_number: Mapped[str | None] = mapped_column(String(80))
    amount_cents: Mapped[int | None] = mapped_column(Integer)
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class BenefitItem(TenantMixin, Base):
    """Item que o programa oferece; `requires_attendance` limita a entrega aos presentes no encontro (ex.: lanche)."""

    __tablename__ = "benefit_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[BenefitKind] = mapped_column(SAEnum(BenefitKind), default=BenefitKind.other)
    unit: Mapped[str] = mapped_column(String(40), default="unidade")
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    requires_attendance: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class BenefitStockEntry(TenantMixin, Base):
    """Entrada de estoque (compra ou doacao), com custo e financiador."""

    __tablename__ = "benefit_stock_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("benefit_items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    origin: Mapped[StockOrigin] = mapped_column(SAEnum(StockOrigin), default=StockOrigin.purchase)
    funding_source_id: Mapped[UUID | None] = mapped_column(ForeignKey("funding_sources.id"), index=True)
    received_on: Mapped[date] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    item: Mapped["BenefitItem"] = relationship()


class BenefitDelivery(TenantMixin, Base):
    """Entrega ao aluno; o custo unitario fica congelado para a prestacao de contas."""

    __tablename__ = "benefit_deliveries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("benefit_items.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    class_offering_id: Mapped[UUID] = mapped_column(ForeignKey("class_offerings.id"), index=True)
    scheduled_meeting_id: Mapped[UUID | None] = mapped_column(ForeignKey("scheduled_meetings.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    delivered_on: Mapped[date] = mapped_column(Date)
    delivered_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    item: Mapped["BenefitItem"] = relationship()
    student: Mapped["Student"] = relationship(foreign_keys=[student_id])
