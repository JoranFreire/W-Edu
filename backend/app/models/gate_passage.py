"""Passagens pela catraca avisadas pelo Persona: base do aviso ao aluno e ao responsavel.

So o necessario (quem, portao, sentido, quando); nada biometrico. O ``jti`` do aviso e unico:
o Persona reenvia em caso de falha, e o mesmo aviso nao gera dois avisos.
"""

from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.ids import new_id
from app.core.tenancy import TenantMixin


class GatePassage(TenantMixin, Base):
    __tablename__ = "gate_passages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    gate: Mapped[str] = mapped_column(String(120))
    direction: Mapped[str] = mapped_column(String(10))  # entry | exit
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship()
