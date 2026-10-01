from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.saas import SaasPlan
from app.repositories.saas import SaasPlanRepository
from app.schemas.saas import SaasPlanCreate, SaasPlanUpdate
from app.services.academic.errors import conflict, not_found
from app.services.academic.patch import apply_patch


class SaasPlanService:
    """Catalogo de planos da plataforma (super admin)."""

    def __init__(self, db: Session):
        self.repo = SaasPlanRepository(db)

    def list(self) -> list[SaasPlan]:
        return self.repo.list()

    def public(self) -> list[SaasPlan]:
        """Planos oferecidos na pagina de contratacao: so os ativos, do mais barato ao mais caro."""
        return sorted((plan for plan in self.repo.list() if plan.is_active), key=lambda plan: plan.monthly_price_cents)

    def get_or_404(self, plan_id: UUID) -> SaasPlan:
        plan = self.repo.get_by_id(plan_id)
        if not plan:
            raise not_found("Plano não encontrado")
        return plan

    def create(self, data: SaasPlanCreate) -> SaasPlan:
        if self.repo.get_by_name(data.name):
            raise conflict("Já existe plano com este nome")
        return self.repo.save(SaasPlan(**data.model_dump()))

    def update(self, plan_id: UUID, data: SaasPlanUpdate) -> SaasPlan:
        plan = self.get_or_404(plan_id)
        if data.name and data.name != plan.name and self.repo.get_by_name(data.name):
            raise conflict("Já existe plano com este nome")
        apply_patch(plan, data, clearable=frozenset({"description", "max_students"}))
        return self.repo.save(plan)
