from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.completion import Internship, ReviewStatus
from app.models.student import Student
from app.policies.completion_access import ensure_active, ensure_advisor_role
from app.repositories.completion import InternshipRepository
from app.repositories.student import StudentRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.completion import InternshipCreate, InternshipOut, InternshipUpdate
from app.services.academic.errors import bad_request, not_found
from app.services.academic.patch import apply_patch
from app.services.secretariat.lifecycle import EnrollmentLifecycleService

CLEARABLE = frozenset({"supervisor_name", "advisor_id", "agreement_number", "ends_on", "planned_hours", "notes"})


class InternshipService:
    """Estagios do aluno, cadastrados pela secretaria com o orientador da instituicao."""

    def __init__(self, db: Session):
        self.repo = InternshipRepository(db)
        self.users = StudentRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def list_for_enrollment(self, enrollment_id: UUID) -> list[InternshipOut]:
        self.lifecycle.get_or_404(enrollment_id)
        return self.to_out(self.repo.list_by_enrollment(enrollment_id))

    def list_mine(self, student: Student) -> list[InternshipOut]:
        return self.to_out(self.repo.list_by_student(student.id))

    def create(self, enrollment_id: UUID, data: InternshipCreate) -> InternshipOut:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        ensure_active(enrollment)
        internship = Internship(program_enrollment_id=enrollment.id, **data.model_dump())
        self._validate(internship)
        return self.to_out([self.repo.save(internship)])[0]

    def update(self, internship_id: UUID, data: InternshipUpdate) -> InternshipOut:
        internship = self.get_or_404(internship_id)
        apply_patch(internship, data, clearable=CLEARABLE)
        self._validate(internship)
        return self.to_out([self.repo.save(internship)])[0]

    def get_or_404(self, internship_id: UUID) -> Internship:
        internship = self.repo.get_by_id(internship_id)
        if not internship:
            raise not_found("Estágio não encontrado")
        return internship

    def to_out(self, internships: list[Internship]) -> list[InternshipOut]:
        hours = self.repo.hours([internship.id for internship in internships])
        return [
            InternshipOut(
                id=i.id, program_enrollment_id=i.program_enrollment_id, student=PersonSummary.model_validate(i.program_enrollment.student),
                company_name=i.company_name, supervisor_name=i.supervisor_name,
                advisor=PersonSummary.model_validate(i.advisor) if i.advisor else None, is_mandatory=i.is_mandatory,
                agreement_number=i.agreement_number, starts_on=i.starts_on, ends_on=i.ends_on, planned_hours=i.planned_hours,
                status=i.status, notes=i.notes,
                approved_hours=hours.get(i.id, {}).get(ReviewStatus.approved, 0),
                pending_hours=hours.get(i.id, {}).get(ReviewStatus.submitted, 0),
            )
            for i in internships
        ]

    def _validate(self, internship: Internship) -> None:
        if internship.ends_on and internship.ends_on < internship.starts_on:
            raise bad_request("O término não pode ser anterior ao início")
        if internship.advisor_id is not None:
            advisor = self.users.get_by_id(internship.advisor_id)
            if not advisor:
                raise not_found("Orientador não encontrado")
            ensure_advisor_role(advisor)
