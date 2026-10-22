from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GateNoticeIn(BaseModel):
    """Aviso de passagem assinado pelo Persona (`typ=gate_event`)."""

    notice: str = Field(min_length=10, max_length=4000)


class GateNoticeOut(BaseModel):
    # recorded: novo; duplicate: o mesmo aviso ja tinha chegado; ignored: a pessoa nao e (mais) da instituicao.
    # Todos respondem 200: o Persona reenvia em qualquer erro, e nenhum desses casos melhora reenviando.
    status: Literal["recorded", "duplicate", "ignored"]


class MembershipEventOut(BaseModel):
    id: UUID
    user_id: UUID
    kind: Literal["ended"]
    occurred_at: datetime
