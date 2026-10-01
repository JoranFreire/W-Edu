"""Valores de referencia nacionais guardados localmente (tabela global, sem instituicao)."""

from uuid import UUID

from app.core.ids import new_id
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MinimumWageValue(Base):
    """Salario minimo vigente a partir de `valid_from`; espelho da serie 1619 do SGS do Banco Central."""

    __tablename__ = "minimum_wage_values"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    valid_from: Mapped[date] = mapped_column(Date, unique=True, index=True)
    cents: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(20), default="bcb")   # "bcb" ou "seed" (carga inicial)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
