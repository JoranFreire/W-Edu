"""Assinatura de integridade (HMAC-SHA256 com a SECRET_KEY) para documentos emitidos."""

from datetime import datetime, timezone
import hashlib
import hmac
import secrets

from app.core.config import settings

ALGORITHM = "HMAC-SHA256"


def sign(parts: list[str]) -> str:
    payload = "|".join(parts)
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def verify(signature: str | None, parts: list[str]) -> bool:
    return bool(signature) and hmac.compare_digest(signature, sign(parts))


def validation_code() -> str:
    """Codigo publico curto e sem simbolos, para validar o documento na internet."""
    return secrets.token_urlsafe(12).replace("-", "").replace("_", "")


def timestamp(value: datetime) -> str:
    """Instante canonico para assinar: UTC, sem fuso e em segundos (igual em qualquer banco)."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="seconds")
