from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.tuition import TuitionBasis, TuitionPlan
from app.repositories.academic import ClassGroupMemberRepository, ProgramEnrollmentRepository
from app.services.registration.plan import TermPlanBuilder


@dataclass(frozen=True)
class BillingTarget:
    enrollment: ProgramEnrollment
    credits: int | None   # creditos inscritos no periodo (so no plano por credito)


class BillingTargets:
    """Quem o plano cobra: matriculas ativas no programa, alunos da turma-grupo ou inscritos em creditos no periodo."""

    def __init__(self, db: Session):
        self.enrollments = ProgramEnrollmentRepository(db)
        self.members = ClassGroupMemberRepository(db)
        self.plans = TermPlanBuilder(db)

    def for_plan(self, plan: TuitionPlan) -> list[BillingTarget]:
        if plan.basis == TuitionBasis.class_group:
            members = self.members.list_by_group(plan.class_group_id)
            return [BillingTarget(m.program_enrollment, None) for m in members if m.program_enrollment.status == ProgramEnrollmentStatus.active]
        active = self.enrollments.list(program_id=plan.program_id, status=ProgramEnrollmentStatus.active)
        if plan.basis == TuitionBasis.program:
            return [BillingTarget(enrollment, None) for enrollment in active]
        targets = []
        for enrollment in active:
            credits = self.plans.build(enrollment, plan.term_id, []).registered_credits()
            if credits > 0:
                targets.append(BillingTarget(enrollment, credits))
        return targets
