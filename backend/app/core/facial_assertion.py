"""Assertion do login facial emitido pelo Persona (`typ=facial_login`).

O Persona confere o rosto (1:1, com prova de vida) e assina um assertion curto dizendo
"esta pessoa, nesta instituicao". A conferencia comum (assinatura, tipo, prazo) fica em
``persona_message``; o uso unico (``jti``) fica com o servico, que precisa do banco.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from app.core.persona_message import InvalidPersonaMessage, expiry_of, verify_message

TYPE = "facial_login"


@dataclass(frozen=True)
class FacialAssertion:
    user_id: UUID
    institution_id: UUID
    jti: str
    expires_at: datetime


def verify_assertion(token: str, public_key: Ed25519PublicKey, now: datetime | None = None) -> FacialAssertion:
    claims = verify_message(token, public_key, TYPE, now)
    try:
        return FacialAssertion(
            user_id=UUID(str(claims["sub"])),
            institution_id=UUID(str(claims["inst"])),
            jti=str(claims["jti"]),
            expires_at=expiry_of(claims),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPersonaMessage("claims incompletas") from exc
