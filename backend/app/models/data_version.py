"""Versao dos dados de cada area por instituicao, para o cache dos apps.

O app guarda as telas em disco e so as baixa de novo quando a versao da area muda.
A versao sobe sozinha a cada gravacao nas tabelas da area (``app.core.change_tracking``).
"""

from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.ids import new_id
from app.core.tenancy import TenantMixin


class DataVersion(TenantMixin, Base):
    __tablename__ = "data_versions"
    __table_args__ = (UniqueConstraint("institution_id", "area"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    area: Mapped[str] = mapped_column(String(40))
    version: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
