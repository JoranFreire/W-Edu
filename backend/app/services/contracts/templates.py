from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.contracts import ContractTemplate
from app.repositories.contracts import ContractTemplateRepository
from app.schemas.contracts import ContractTemplateCreate, ContractTemplateUpdate
from app.services.academic.errors import bad_request, not_found
from app.services.academic.patch import apply_patch
from app.services.contracts.fields import FIELDS
from app.services.notifications.templates import render_template


class ContractTemplateService:
    """Modelos de contrato de matricula e rematricula da instituicao."""

    def __init__(self, db: Session):
        self.repo = ContractTemplateRepository(db)

    def list(self) -> list[ContractTemplate]:
        return self.repo.list()

    def get_or_404(self, template_id: UUID) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise not_found("Modelo de contrato não encontrado")
        return template

    def create(self, data: ContractTemplateCreate) -> ContractTemplate:
        self._validate_body(data.body)
        return self.repo.save(ContractTemplate(**data.model_dump()))

    def update(self, template_id: UUID, data: ContractTemplateUpdate) -> ContractTemplate:
        template = self.get_or_404(template_id)
        if data.body is not None:
            self._validate_body(data.body)
        apply_patch(template, data)
        return self.repo.save(template)

    @staticmethod
    def _validate_body(body: str) -> None:
        """Chaves soltas quebram o preenchimento; campos desconhecidos so ficam vazios."""
        try:
            render_template(body, {field: "" for field in FIELDS})
        except (ValueError, IndexError) as exc:
            raise bad_request("Texto do modelo com chaves inválidas: use {campo} ou {{ e }} para chaves literais") from exc
