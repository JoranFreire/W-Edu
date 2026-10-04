"""Assertion do login facial emitido pelo Persona (JWS compacto, EdDSA/Ed25519 — RFC 8037).

O Persona confere o rosto (1:1, com prova de vida) e assina um assertion curto dizendo
"esta pessoa, nesta instituicao". O W-Edu so tem a chave publica: confere a assinatura e
os prazos aqui; o uso unico (``jti``) fica com o servico, que precisa do banco.
O python-jose instalado nao suporta EdDSA, por isso a verificacao e feita direto com
``cryptography``.
"""

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ISSUER = "persona"
AUDIENCE = "wedu"
# O Persona assina outras mensagens com a mesma chave (aviso de catraca, `gate_event`):
# so `facial_login` vale como login.
TYPE = "facial_login"
MAX_LIFETIME_SECONDS = 60
CLOCK_SKEW_SECONDS = 5


class InvalidAssertion(Exception):
    """Assinatura, formato ou prazo invalido."""


@dataclass(frozen=True)
class FacialAssertion:
    user_id: UUID
    institution_id: UUID
    jti: str
    expires_at: datetime


def _b64decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def load_public_key(encoded: str) -> Ed25519PublicKey:
    """Chave publica Ed25519 crua (32 bytes) em base64url, como o Persona a exporta."""
    return Ed25519PublicKey.from_public_bytes(_b64decode(encoded.strip()))


def verify_assertion(token: str, public_key: Ed25519PublicKey, now: datetime | None = None) -> FacialAssertion:
    now = now or datetime.now(timezone.utc)
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        header = json.loads(_b64decode(header_b64))
        if header.get("alg") != "EdDSA":
            raise InvalidAssertion("algoritmo inesperado")
        public_key.verify(_b64decode(signature_b64), f"{header_b64}.{payload_b64}".encode("ascii"))
        claims = json.loads(_b64decode(payload_b64))
    except (ValueError, InvalidSignature) as exc:
        raise InvalidAssertion("assertion invalido") from exc

    if claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
        raise InvalidAssertion("emissor ou destino inesperado")
    if claims.get("typ") != TYPE:
        raise InvalidAssertion("mensagem do Persona que nao e login")
    try:
        issued_at = datetime.fromtimestamp(int(claims["iat"]), timezone.utc)
        expires_at = datetime.fromtimestamp(int(claims["exp"]), timezone.utc)
        assertion = FacialAssertion(
            user_id=UUID(str(claims["sub"])),
            institution_id=UUID(str(claims["inst"])),
            jti=str(claims["jti"]),
            expires_at=expires_at,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidAssertion("claims incompletas") from exc

    if (expires_at - issued_at).total_seconds() > MAX_LIFETIME_SECONDS:
        raise InvalidAssertion("validade longa demais")
    if now.timestamp() > expires_at.timestamp() + CLOCK_SKEW_SECONDS:
        raise InvalidAssertion("assertion vencido")
    if issued_at.timestamp() > now.timestamp() + CLOCK_SKEW_SECONDS:
        raise InvalidAssertion("assertion emitido no futuro")
    if not assertion.jti:
        raise InvalidAssertion("sem jti")
    return assertion
