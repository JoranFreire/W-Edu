from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.schemas.secretariat import ConclusionCheckOut
from app.services.academic.errors import bad_request, conflict
from app.services.secretariat.lifecycle import EnrollmentLifecycleService
from app.services.secretariat.transcript import TranscriptService


class ConclusionService:
    """Conclusao do programa: exige a carga obrigatoria cumprida (e a carga total do programa, se definida)."""

    def __init__(self, db: Session):
        self.lifecycle = EnrollmentLifecycleService(db)
        self.transcripts = TranscriptService(db)

    def check(self, enrollment_id: int) -> ConclusionCheckOut:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        summary = self.transcripts.for_enrollment(enrollment_id).summary
        required = enrollment.program.total_hours
        missing = []
        if enrollment.status != ProgramEnrollmentStatus.active:
            missing.append("A matrícula precisa estar ativa")
        if summary.integralization < 100:
            missing.append(f"Carga obrigatória cumprida: {summary.integralization:g}%")
        if required is not None and summary.hours_done < required:
            missing.append(f"Carga horária total: {summary.hours_done}h de {required}h")
        return ConclusionCheckOut(
            eligible=not missing, status=enrollment.status.value, integralization=summary.integralization,
            hours_done=summary.hours_done, required_hours=required, missing=missing,
        )

    def conclude(self, enrollment_id: int, concluded_on: date, ceremony_on: date | None, user_id: int) -> ProgramEnrollment:
        check = self.check(enrollment_id)
        if not check.eligible:
            raise conflict("Requisitos pendentes: " + "; ".join(check.missing))
        self._validate_dates(concluded_on, ceremony_on)
        enrollment = self.lifecycle.transition(
            enrollment_id, ProgramEnrollmentStatus.graduated, user_id,
            details={"concluded_on": concluded_on.isoformat(), "ceremony_on": ceremony_on.isoformat() if ceremony_on else None},
            commit=False,
        )
        enrollment.concluded_on, enrollment.ceremony_on = concluded_on, ceremony_on
        return self.lifecycle.repo.save(enrollment)

    def set_ceremony(self, enrollment_id: int, ceremony_on: date) -> ProgramEnrollment:
        """Colacao de grau registrada depois da conclusao."""
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        if enrollment.status != ProgramEnrollmentStatus.graduated:
            raise conflict("Só programas concluídos têm colação de grau")
        self._validate_dates(enrollment.concluded_on, ceremony_on)
        enrollment.ceremony_on = ceremony_on
        return self.lifecycle.repo.save(enrollment)

    @staticmethod
    def _validate_dates(concluded_on: date | None, ceremony_on: date | None) -> None:
        if concluded_on and ceremony_on and ceremony_on < concluded_on:
            raise bad_request("A colação não pode ser anterior à conclusão")
