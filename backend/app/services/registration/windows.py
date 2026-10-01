from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.course_registration import RegistrationWindow
from app.repositories.academic import AcademicTermRepository, ProgramRepository
from app.repositories.registration import RegistrationWindowRepository
from app.schemas.course_registration import RegistrationWindowCreate, RegistrationWindowOut, RegistrationWindowUpdate
from app.services.academic.errors import bad_request, not_found
from app.services.registration.rules import as_utc, window_is_open


def is_open(window: RegistrationWindow) -> bool:
    return window_is_open(window.opens_at, window.closes_at, datetime.now(timezone.utc))


def to_out(window: RegistrationWindow) -> RegistrationWindowOut:
    return RegistrationWindowOut(
        id=window.id, term_id=window.term_id, term_name=window.term.name, program_id=window.program_id,
        program_name=window.program.name if window.program else None, name=window.name,
        opens_at=window.opens_at, closes_at=window.closes_at, min_credits=window.min_credits,
        max_credits=window.max_credits, allow_waitlist=window.allow_waitlist, is_open=is_open(window),
    )


class RegistrationWindowService:
    """Janelas de matricula por disciplina, mantidas pela secretaria e coordenacao."""

    def __init__(self, db: Session):
        self.repo = RegistrationWindowRepository(db)
        self.terms = AcademicTermRepository(db)
        self.programs = ProgramRepository(db)

    def list(self, term_id: int | None = None) -> list[RegistrationWindowOut]:
        return [to_out(window) for window in self.repo.list(term_id)]

    def get_or_404(self, window_id: int) -> RegistrationWindow:
        window = self.repo.get_by_id(window_id)
        if not window:
            raise not_found("Janela de matrícula não encontrada")
        return window

    def create(self, data: RegistrationWindowCreate) -> RegistrationWindowOut:
        if not self.terms.get_by_id(data.term_id):
            raise not_found("Período letivo não encontrado")
        if data.program_id is not None and not self.programs.get_by_id(data.program_id):
            raise not_found("Programa não encontrado")
        window = RegistrationWindow(**data.model_dump())
        self._normalize(window)
        self._validate(window)
        return to_out(self.repo.save(window))

    def update(self, window_id: int, data: RegistrationWindowUpdate) -> RegistrationWindowOut:
        window = self.get_or_404(window_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(window, field, value)
        self._normalize(window)
        self._validate(window)
        return to_out(self.repo.save(window))

    def delete(self, window_id: int) -> None:
        self.repo.delete(self.get_or_404(window_id))

    @staticmethod
    def _normalize(window: RegistrationWindow) -> None:
        window.opens_at, window.closes_at = as_utc(window.opens_at), as_utc(window.closes_at)

    @staticmethod
    def _validate(window: RegistrationWindow) -> None:
        if as_utc(window.closes_at) <= as_utc(window.opens_at):
            raise bad_request("O fechamento deve ser posterior à abertura")
        if window.min_credits is not None and window.max_credits is not None and window.min_credits > window.max_credits:
            raise bad_request("O mínimo de créditos não pode passar do máximo")
