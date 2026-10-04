"""Rotas de integracao (/integrations/persona): aviso de passagem na catraca e fins de vinculo."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator
from app.models.student import Student
from app.schemas.integrations import GateNoticeIn, GateNoticeOut, MembershipEventOut
from app.services.integrations.gate_passages import GatePassageService
from app.services.integrations.membership_feed import MembershipFeedService

router = APIRouter(prefix="/persona")


@router.post("/gate-events", response_model=GateNoticeOut)
def receive_gate_event(data: GateNoticeIn, db: Session = Depends(get_db)):
    """Sem token: a autenticacao e a assinatura do Persona no proprio aviso."""
    return GateNoticeOut(status=GatePassageService(db).receive(data.notice))


@router.get("/membership-events", response_model=list[MembershipEventOut])
def membership_events(
    since: datetime | None = None, limit: int = 200,
    db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator),
):
    # Conta de servico do Persona na instituicao (a mesma que devolve a chamada facial).
    return MembershipFeedService(db).since(since, limit)
