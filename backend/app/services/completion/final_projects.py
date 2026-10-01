from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.completion import FinalProject, FinalProjectStatus
from app.models.student import Student
from app.policies.completion_access import ensure_active, ensure_advisor_role, ensure_can_supervise
from app.repositories.completion import FinalProjectRepository
from app.repositories.student import StudentRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.completion import FinalProjectInput, FinalProjectOut, FinalProjectResult
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


def to_out(project: FinalProject) -> FinalProjectOut:
    return FinalProjectOut(
        id=project.id, program_enrollment_id=project.program_enrollment_id,
        student=PersonSummary.model_validate(project.program_enrollment.student), title=project.title,
        advisor=PersonSummary.model_validate(project.advisor) if project.advisor else None, co_advisor_name=project.co_advisor_name,
        status=project.status, defense_on=project.defense_on, grade=project.grade, committee=project.committee, notes=project.notes,
    )


class FinalProjectService:
    """TCC: a secretaria cadastra tema e orientador; o orientador (ou a coordenacao) registra entrega e defesa."""

    def __init__(self, db: Session):
        self.repo = FinalProjectRepository(db)
        self.users = StudentRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def get_for_enrollment(self, enrollment_id: int) -> FinalProjectOut | None:
        self.lifecycle.get_or_404(enrollment_id)
        project = self.repo.get_by_enrollment(enrollment_id)
        return to_out(project) if project else None

    def list_mine(self, student: Student) -> list[FinalProjectOut]:
        return [to_out(project) for project in self.repo.list_by_student(student.id)]

    def save(self, enrollment_id: int, data: FinalProjectInput) -> FinalProjectOut:
        """Cria ou atualiza; depois de reprovado, salvar de novo abre nova tentativa."""
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        ensure_active(enrollment)
        if data.advisor_id is not None:
            advisor = self.users.get_by_id(data.advisor_id)
            if not advisor:
                raise not_found("Orientador não encontrado")
            ensure_advisor_role(advisor)
        project = self.repo.get_by_enrollment(enrollment.id) or FinalProject(program_enrollment_id=enrollment.id)
        if project.status == FinalProjectStatus.approved:
            raise conflict("TCC já aprovado")
        if project.status == FinalProjectStatus.failed:
            project.status, project.defense_on, project.grade, project.committee = FinalProjectStatus.in_progress, None, None, None
        for field, value in data.model_dump().items():
            setattr(project, field, value)
        return to_out(self.repo.save(project))

    def record(self, project_id: int, data: FinalProjectResult, user: Student) -> FinalProjectOut:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise not_found("TCC não encontrado")
        ensure_can_supervise(user, project.advisor_id)
        if project.status in (FinalProjectStatus.approved, FinalProjectStatus.failed):
            raise conflict("TCC já avaliado")
        status = FinalProjectStatus(data.status)
        if status != FinalProjectStatus.submitted and data.defense_on is None:
            raise bad_request("Informe a data da defesa")
        project.status = status
        if status != FinalProjectStatus.submitted:
            project.defense_on, project.grade, project.committee = data.defense_on, data.grade, data.committee
        return to_out(self.repo.save(project))
