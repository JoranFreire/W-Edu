"""Mensagens assinadas pelo Persona (JWS compacto, EdDSA/Ed25519 — RFC 8037).

O Persona assina com a mesma chave mensagens de tipos diferentes (`typ`): o login facial
(`facial_login`) e o aviso de passagem na catraca (`gate_event`). Aqui fica o que vale para
todas: assinatura, emissor, destino, tipo esperado e prazo curto. Cada tipo le as proprias
claims em seu modulo (`facial_assertion.py`, `gate_notice.py`). O W-Edu so tem a chave
publica; o python-jose instalado nao suporta EdDSA, por isso a verificacao e feita com
``cryptography``.
"""

import base64
import json
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ISSUER = "persona"
AUDIENCE = "wedu"
MAX_LIFETIME_SECONDS = 60
CLOCK_SKEW_SECONDS = 5


class InvalidPersonaMessage(Exception):
    """Assinatura, formato, tipo ou prazo invalido."""


def _b64decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def load_public_key(encoded: str) -> Ed25519PublicKey:
    """Chave publica Ed25519 crua (32 bytes) em base64url, como o Persona a exporta."""
    return Ed25519PublicKey.from_public_bytes(_b64decode(encoded.strip()))


def verify_message(token: str, public_key: Ed25519PublicKey, expected_type: str, now: datetime | None = None) -> dict:
    """Claims da mensagem, se assinada pelo Persona, do tipo esperado, com `jti` e dentro do prazo."""
    now = now or datetime.now(timezone.utc)
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        header = json.loads(_b64decode(header_b64))
        if header.get("alg") != "EdDSA":
            raise InvalidPersonaMessage("algoritmo inesperado")
        public_key.verify(_b64decode(signature_b64), f"{header_b64}.{payload_b64}".encode("ascii"))
        claims = json.loads(_b64decode(payload_b64))
    except (ValueError, InvalidSignature) as exc:
        raise InvalidPersonaMessage("mensagem invalida") from exc
    if not isinstance(claims, dict):
        raise InvalidPersonaMessage("mensagem invalida")

    if claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
        raise InvalidPersonaMessage("emissor ou destino inesperado")
    # A mesma chave assina login e aviso de catraca: um nunca vale pelo outro.
    if claims.get("typ") != expected_type:
        raise InvalidPersonaMessage("tipo de mensagem inesperado")
    try:
        issued_at, expires_at = int(claims["iat"]), int(claims["exp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPersonaMessage("sem prazo") from exc
    if expires_at - issued_at > MAX_LIFETIME_SECONDS:
        raise InvalidPersonaMessage("validade longa demais")
    if now.timestamp() > expires_at + CLOCK_SKEW_SECONDS:
        raise InvalidPersonaMessage("mensagem vencida")
    if issued_at > now.timestamp() + CLOCK_SKEW_SECONDS:
        raise InvalidPersonaMessage("mensagem emitida no futuro")
    if not claims.get("jti"):
        raise InvalidPersonaMessage("sem jti")
    return claims


def expiry_of(claims: dict) -> datetime:
    return datetime.fromtimestamp(int(claims["exp"]), timezone.utc)
