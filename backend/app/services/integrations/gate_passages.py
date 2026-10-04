from __future__ import annotations

from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.gate_notice import GateNotice, verify_gate_notice
from app.core.persona_message import InvalidPersonaMessage, load_public_key
from app.core.tenancy import bind_institution
from app.models.gate_passage import GatePassage
from app.models.notification import NotificationEventType
from app.repositories.guardians import GuardianLinkRepository
from app.repositories.integrations import ActiveMemberRepository, GatePassageRepository
from app.repositories.student import StudentRepository
from app.services.notifications.events import NotificationEventService

DIRECTION_LABELS = {"entry": "entrada", "exit": "saída"}


class GatePassageService:
    """Recebe o aviso de passagem do Persona: confere, registra uma vez e avisa o aluno e os responsaveis."""

    def __init__(self, db: Session):
        self.db = db
        self.passages = GatePassageRepository(db)
        self.members = ActiveMemberRepository(db)

    def receive(self, token: str) -> str:
        notice = self._verify(token)
        if not self.members.is_active_member(notice.institution_id, notice.student_id):
            return "ignored"
        # A partir daqui tudo e da instituicao do aviso (filtro de tenant e RLS).
        bind_institution(self.db, notice.institution_id)
        recorded = self.passages.add_once(GatePassage(
            institution_id=notice.institution_id, jti=notice.jti, student_id=notice.student_id,
            gate=notice.gate, direction=notice.direction, occurred_at=notice.occurred_at,
        ))
        if not recorded:
            return "duplicate"
        self._notify(notice)
        self.db.commit()
        return "recorded"

    def _verify(self, token: str) -> GateNotice:
        if not settings.PERSONA_ASSERTION_PUBLIC_KEY:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Integração com o Persona desativada")
        try:
            return verify_gate_notice(token, load_public_key(settings.PERSONA_ASSERTION_PUBLIC_KEY))
        except InvalidPersonaMessage:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Aviso de passagem inválido")

    def _notify(self, notice: GateNotice) -> None:
        student = StudentRepository(self.db).get_by_id(notice.student_id)
        local = notice.occurred_at.astimezone(ZoneInfo(settings.DISPLAY_TIMEZONE))
        payload = {
            "student_name": student.name if student else "Aluno", "gate": notice.gate,
            "direction_label": DIRECTION_LABELS[notice.direction], "time": local.strftime("%H:%M"), "date": local.strftime("%d/%m/%Y"),
        }
        guardians = [link.guardian_id for link in GuardianLinkRepository(self.db).list_by_student(notice.student_id)]
        events = NotificationEventService(self.db)
        for recipient in [notice.student_id, *guardians]:
            events.publish(NotificationEventType.gate_passage, payload, recipient_student_id=recipient)
