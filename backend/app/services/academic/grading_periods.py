from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_calendar import AcademicTerm, GradingPeriod, GradingPeriodStatus, TermStatus
from app.repositories.academic import GradingPeriodRepository
from app.schemas.academic_calendar import GradingPeriodCreate, GradingPeriodUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.terms import AcademicTermService


class GradingPeriodService:
    """Etapas de avaliacao (bimestres, trimestres, N1/N2) dentro de um periodo letivo."""

    def __init__(self, db: Session):
        self.repo = GradingPeriodRepository(db)
        self.terms = AcademicTermService(db)

    def list(self, term_id: UUID) -> list[GradingPeriod]:
        self.terms.get_or_404(term_id)
        return self.repo.list_by_term(term_id)

    def create(self, term_id: UUID, data: GradingPeriodCreate) -> GradingPeriod:
        term = self.terms.get_not_closed(term_id)
        existing = self.repo.list_by_term(term_id)
        order = data.order or max((p.order for p in existing), default=0) + 1
        if any(p.order == order for p in existing):
            raise conflict("Já existe etapa com esta ordem")
        period = GradingPeriod(term_id=term_id, **{**data.model_dump(), "order": order})
        self._validate_dates(term, period, existing)
        return self.repo.save(period)

    def update(self, period_id: UUID, data: GradingPeriodUpdate) -> GradingPeriod:
        period = self._get_editable(period_id)
        apply_patch(period, data)
        if period.ends_on < period.starts_on:
            raise bad_request("A data final não pode ser anterior à inicial")
        others = [p for p in self.repo.list_by_term(period.term_id) if p.id != period.id]
        self._validate_dates(period.term, period, others)
        return self.repo.save(period)

    def change_status(self, period_id: UUID, target: GradingPeriodStatus) -> GradingPeriod:
        period = self.get_or_404(period_id)
        if target == GradingPeriodStatus.open and period.term.status == TermStatus.closed:
            raise conflict("Período letivo encerrado; reabra-o antes da etapa")
        period.status = target
        return self.repo.save(period)

    def delete(self, period_id: UUID) -> None:
        self.repo.delete(self._get_editable(period_id))

    def get_or_404(self, period_id: UUID) -> GradingPeriod:
        period = self.repo.get_by_id(period_id)
        if not period:
            raise not_found("Etapa de avaliação não encontrada")
        return period

    def _get_editable(self, period_id: UUID) -> GradingPeriod:
        period = self.get_or_404(period_id)
        if period.status == GradingPeriodStatus.closed:
            raise conflict("Etapa encerrada")
        return period

    @staticmethod
    def _validate_dates(term: AcademicTerm, period: GradingPeriod, others: list[GradingPeriod]) -> None:
        if period.starts_on < term.starts_on or period.ends_on > term.ends_on:
            raise bad_request("A etapa precisa estar dentro do período letivo")
        if any(p.starts_on <= period.ends_on and period.starts_on <= p.ends_on for p in others):
            raise bad_request("A etapa se sobrepõe a outra etapa do período")
