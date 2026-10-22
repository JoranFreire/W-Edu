"""Fim de vinculo com a instituicao, para os sistemas integrados (Persona) revogarem acessos.

Registrado sozinho (``app.core.membership_events``) quando o vinculo e desativado ou removido, ou
a conta e desativada. Tabela da plataforma, como ``institution_memberships`` (sem RLS): uma conta
desativada numa instituicao encerra os vinculos em todas.
"""

from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.ids import new_id


class MembershipEvent(Base):
    __tablename__ = "membership_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    institution_id: Mapped[UUID] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(index=True)  # sem FK: a conta pode ter sido excluida
    kind: Mapped[str] = mapped_column(String(20), default="ended")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
