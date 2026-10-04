from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FacialLoginAssertion(Base):
    """Assertions de login facial ja usados: o ``jti`` entra uma vez so (barra replay).

    Tabela da plataforma, sem instituicao (como ``users``): o assertion e consumido antes
    de haver instituicao vinculada a requisicao.
    """

    __tablename__ = "facial_login_assertions"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
