from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tuition import TuitionBasis, TuitionPlan
from app.repositories.academic import AcademicTermRepository, ClassGroupRepository, ProgramRepository
from app.repositories.tuition import TuitionPlanRepository
from app.schemas.tuition import TuitionPlanCreate, TuitionPlanOut, TuitionPlanUpdate
from app.services.academic.errors import bad_request, not_found
from app.services.academic.patch import apply_patch


def to_out(plan: TuitionPlan) -> TuitionPlanOut:
    return TuitionPlanOut(
        id=plan.id, name=plan.name, basis=plan.basis, term_id=plan.term_id, term_name=plan.term.name,
        program_id=plan.program_id, program_name=plan.program.name if plan.program else None,
        class_group_id=plan.class_group_id, class_group_name=plan.class_group.name if plan.class_group else None,
        amount_cents=plan.amount_cents, installments=plan.installments, first_due_on=plan.first_due_on, is_active=plan.is_active,
    )


class TuitionPlanService:
    """Planos de mensalidade por programa, turma-grupo ou credito, num periodo letivo."""

    def __init__(self, db: Session):
        self.repo = TuitionPlanRepository(db)
        self.terms = AcademicTermRepository(db)
        self.programs = ProgramRepository(db)
        self.groups = ClassGroupRepository(db)

    def list(self, term_id: UUID | None = None) -> list[TuitionPlanOut]:
        return [to_out(plan) for plan in self.repo.list(term_id)]

    def get_or_404(self, plan_id: UUID) -> TuitionPlan:
        plan = self.repo.get_by_id(plan_id)
        if not plan:
            raise not_found("Plano de mensalidade não encontrado")
        return plan

    def create(self, data: TuitionPlanCreate) -> TuitionPlanOut:
        if not self.terms.get_by_id(data.term_id):
            raise not_found("Período letivo não encontrado")
        plan = TuitionPlan(**data.model_dump())
        self._validate_target(plan)
        return to_out(self.repo.save(plan))

    def update(self, plan_id: UUID, data: TuitionPlanUpdate) -> TuitionPlanOut:
        plan = self.get_or_404(plan_id)
        apply_patch(plan, data)
        return to_out(self.repo.save(plan))

    def _validate_target(self, plan: TuitionPlan) -> None:
        """Programa e turma-grupo exigem o alvo; por credito, o programa e opcional (vazio: todos)."""
        if plan.basis == TuitionBasis.class_group:
            group = self.groups.get_by_id(plan.class_group_id) if plan.class_group_id else None
            if not group:
                raise bad_request("Informe a turma-grupo do plano")
            if group.term_id != plan.term_id:
                raise bad_request("A turma-grupo é de outro período letivo")
            plan.program_id = group.program_id
            return
        plan.class_group_id = None
        if plan.basis == TuitionBasis.program and plan.program_id is None:
            raise bad_request("Informe o programa do plano")
        if plan.program_id is not None and not self.programs.get_by_id(plan.program_id):
            raise not_found("Programa não encontrado")
