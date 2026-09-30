from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_calendar import AcademicTerm, GradingPeriodStatus, TermStatus
from app.repositories.academic import AcademicTermRepository
from app.schemas.academic_calendar import AcademicTermCreate, AcademicTermUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.transitions import can_change_term


class AcademicTermService:
    """Periodos letivos: planejado -> aberto -> encerrado (com reabertura)."""

    def __init__(self, db: Session):
        self.repo = AcademicTermRepository(db)

    def list(self) -> list[AcademicTerm]:
        return self.repo.list_all()

    def get_or_404(self, term_id: int) -> AcademicTerm:
        term = self.repo.get_by_id(term_id)
        if not term:
            raise not_found("Período letivo não encontrado")
        return term

    def get_not_closed(self, term_id: int) -> AcademicTerm:
        term = self.get_or_404(term_id)
        if term.status == TermStatus.closed:
            raise conflict("Período letivo encerrado")
        return term

    def create(self, data: AcademicTermCreate) -> AcademicTerm:
        self._ensure_unique_name(data.name)
        return self.repo.save(AcademicTerm(**data.model_dump()))

    def update(self, term_id: int, data: AcademicTermUpdate) -> AcademicTerm:
        term = self.get_not_closed(term_id)
        if data.name is not None and data.name != term.name:
            self._ensure_unique_name(data.name)
        starts_on, ends_on = data.starts_on or term.starts_on, data.ends_on or term.ends_on
        if ends_on < starts_on:
            raise bad_request("A data final não pode ser anterior à inicial")
        if any(p.starts_on < starts_on or p.ends_on > ends_on for p in term.grading_periods):
            raise bad_request("Etapas de avaliação ficariam fora do período")
        apply_patch(term, data)
        return self.repo.save(term)

    def change_status(self, term_id: int, target: TermStatus) -> AcademicTerm:
        term = self.get_or_404(term_id)
        if not can_change_term(term.status, target):
            raise conflict(f"Transição de {term.status.value} para {target.value} não permitida")
        term.status = target
        if target == TermStatus.closed:
            for period in term.grading_periods:
                period.status = GradingPeriodStatus.closed
        return self.repo.save(term)

    def delete(self, term_id: int) -> None:
        term = self.get_or_404(term_id)
        if term.status != TermStatus.planned:
            raise conflict("Só períodos planejados podem ser excluídos")
        if self.repo.is_referenced(term_id):
            raise conflict("Período possui turmas, matrículas ou ofertas vinculadas")
        self.repo.delete(term)

    def _ensure_unique_name(self, name: str) -> None:
        if self.repo.get_by_name(name):
            raise conflict("Já existe período letivo com este nome")
