from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ClassGroupMember, ProgramEnrollmentStatus
from app.repositories.academic import ClassGroupMemberRepository
from app.schemas.academic_groups import ClassGroupMemberOut, PersonSummary
from app.services.academic.class_groups import ClassGroupService
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.program_enrollments import ProgramEnrollmentService


class ClassGroupMemberService:
    """Alocacao de alunos (matriculas ativas do mesmo programa) nas turmas-grupo."""

    def __init__(self, db: Session):
        self.repo = ClassGroupMemberRepository(db)
        self.groups = ClassGroupService(db)
        self.enrollments = ProgramEnrollmentService(db)

    def list(self, group_id: UUID) -> list[ClassGroupMemberOut]:
        self.groups.get_or_404(group_id)
        return [self._to_out(member) for member in self.repo.list_by_group(group_id)]

    def add(self, group_id: UUID, enrollment_id: UUID) -> ClassGroupMemberOut:
        group = self.groups.get_or_404(group_id)
        self.groups.terms.get_not_closed(group.term_id)
        enrollment = self.enrollments.get_or_404(enrollment_id)
        if enrollment.program_id != group.program_id:
            raise bad_request("A matrícula é de outro programa")
        if enrollment.status != ProgramEnrollmentStatus.active:
            raise bad_request("Só matrículas ativas podem ser alocadas")
        if current := self.repo.group_in_term(enrollment_id, group.term_id):
            raise conflict(f"Aluno já está na turma {current.name} neste período")
        if group.capacity is not None and self.repo.count(group_id) >= group.capacity:
            raise conflict("Turma sem vagas")
        member = self.repo.save(ClassGroupMember(class_group_id=group_id, program_enrollment_id=enrollment_id))
        return self._to_out(member)

    def remove(self, group_id: UUID, enrollment_id: UUID) -> None:
        member = self.repo.get(group_id, enrollment_id)
        if not member:
            raise not_found("Aluno não está nesta turma")
        self.repo.delete(member)

    @staticmethod
    def _to_out(member: ClassGroupMember) -> ClassGroupMemberOut:
        enrollment = member.program_enrollment
        return ClassGroupMemberOut(
            id=member.id,
            program_enrollment_id=enrollment.id,
            registration_number=enrollment.registration_number,
            student=PersonSummary.model_validate(enrollment.student),
        )
