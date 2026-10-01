import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.tenant_host import hostname_of
from app.models.institution import Institution, InstitutionStatus
from app.repositories.institution import InstitutionRepository

_DOMAIN = re.compile(r"^(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")


def normalize_domain(value: str | None) -> str | None:
    """Dominio digitado (com ou sem https://, barra final ou porta) no formato guardado; vazio limpa o dominio."""
    if not value or not value.strip():
        return None
    raw = re.sub(r"^[a-z]+://", "", value.strip().lower()).split("/")[0]
    hostname = hostname_of(raw)
    if not hostname or not _DOMAIN.match(hostname):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Domínio inválido")
    base = (settings.TENANT_BASE_DOMAIN or "").lower().strip(".")
    if base and (hostname == base or hostname.endswith("." + base)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Use o subdomínio da instituição; domínio próprio é um endereço do cliente")
    return hostname


class InstitutionDomainService:
    """Dominio proprio do cliente (ex.: escola.com.br): identifica a instituicao pelo endereco acessado."""

    def __init__(self, db: Session):
        self.repo = InstitutionRepository(db)

    def ref_for_host(self, host: str | None) -> str | None:
        """Slug da instituicao ativa dona do dominio; endereco desconhecido nao corresponde a nenhuma."""
        hostname = hostname_of(host)
        if not hostname:
            return None
        institution = self.repo.get_by_custom_domain(hostname)
        return institution.slug if institution and institution.status == InstitutionStatus.active else None

    def set_custom_domain(self, institution: Institution, value: str | None) -> Institution:
        domain = normalize_domain(value)
        if domain:
            owner = self.repo.get_by_custom_domain(domain)
            if owner and owner.id != institution.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Domínio já usado por outra instituição")
        institution.custom_domain = domain
        return self.repo.update(institution)
