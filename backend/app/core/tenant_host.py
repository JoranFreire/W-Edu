"""Identificacao da instituicao pelo subdominio (ex.: escola-alfa.wedu.com.br)."""

from app.core.config import settings


def hostname_of(host: str | None) -> str | None:
    """Nome do host sem porta, em minusculas (primeiro valor, quando vem de um proxy com varios)."""
    if not host:
        return None
    hostname = host.split(",")[0].strip().split(":")[0].lower().rstrip(".")
    return hostname or None


def slug_from_host(host: str | None, base_domain: str | None = None) -> str | None:
    """Slug do subdominio imediatamente abaixo do dominio base; None fora dele ou em subdominio reservado."""
    base = (base_domain if base_domain is not None else settings.TENANT_BASE_DOMAIN) or ""
    if not host or not base:
        return None
    hostname = hostname_of(host) or ""
    suffix = "." + base.lower().strip(".")
    if not hostname.endswith(suffix):
        return None
    label = hostname[: -len(suffix)]
    if not label or "." in label or label in settings.TENANT_RESERVED_SUBDOMAINS:
        return None
    return label
