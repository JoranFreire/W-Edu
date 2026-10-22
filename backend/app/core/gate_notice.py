"""Aviso de passagem na catraca enviado pelo Persona (`typ=gate_event`, ADR 0014 do Persona).

Diz quem passou (`sub`), em que instituicao (`inst`), por qual portao, em que sentido e quando.
A conferencia comum (assinatura, tipo, prazo) fica em ``persona_message``.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from app.core.persona_message import InvalidPersonaMessage, verify_message

TYPE = "gate_event"
DIRECTIONS = {"ENTRY": "entry", "EXIT": "exit"}


@dataclass(frozen=True)
class GateNotice:
    student_id: UUID
    institution_id: UUID
    jti: str
    gate: str
    direction: str  # "entry" ou "exit"
    occurred_at: datetime


def verify_gate_notice(token: str, public_key: Ed25519PublicKey, now: datetime | None = None) -> GateNotice:
    claims = verify_message(token, public_key, TYPE, now)
    try:
        occurred_at = datetime.fromisoformat(str(claims["at"]))
        if occurred_at.tzinfo is None:
            raise ValueError("horario sem fuso")
        return GateNotice(
            student_id=UUID(str(claims["sub"])),
            institution_id=UUID(str(claims["inst"])),
            jti=str(claims["jti"]),
            gate=str(claims["gate"])[:120],
            direction=DIRECTIONS[str(claims["direction"])],
            occurred_at=occurred_at,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPersonaMessage("aviso de passagem incompleto") from exc
