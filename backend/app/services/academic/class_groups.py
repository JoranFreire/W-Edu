from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.academic_groups import ClassGroup
from app.models.student import ADMIN_ROLES, UserRole
from app.repositories.academic import ClassGroupRepository
from app.repositories.student import StudentRepository
from app.schemas.academic_groups import ClassGroupCreate, ClassGroupOut, ClassGroupUpdate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.academic.programs import ProgramService
from app.services.academic.terms import AcademicTermService
from app.policies.roles import has_any_role

TEACHER_ROLES = ADMIN_ROLES | {UserRole.instructor, UserRole.coordinator}


class ClassGroupService:
    """Turmas-grupo (ex.: 7o ano A) de um programa num periodo letivo."""

    def __init__(self, db: Session):
        self.repo = ClassGroupRepository(db)
        self.students = StudentRepository(db)
        self.programs = ProgramService(db)
        self.terms = AcademicTermService(db)

    def list(self, term_id: UUID | None = None, program_id: UUID | None = None) -> list[ClassGroupOut]:
        groups = self.repo.list(term_id=term_id, program_id=program_id)
        counts = self.repo.member_counts([group.id for group in groups])
        return [self.to_out(group, counts.get(group.id, 0)) for group in groups]

    def get_or_404(self, group_id: UUID) -> ClassGroup:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise not_found("Turma não encontrada")
        return group

    def detail(self, group_id: UUID) -> ClassGroupOut:
        group = self.get_or_404(group_id)
        return self.to_out(group, self.repo.member_counts([group.id]).get(group.id, 0))

    def create(self, data: ClassGroupCreate) -> ClassGroupOut:
        program = self.programs.get_or_404(data.program_id)
        self.terms.get_not_closed(data.term_id)
        self._validate_term_number(program.duration_terms, data.curriculum_term_number)
        self._validate_teacher(data.homeroom_teacher_id)
        if self.repo.get_by_name(data.term_id, data.name):
            raise conflict("Já existe turma com este nome no período")
        return self.to_out(self.repo.save(ClassGroup(**data.model_dump())), 0)

    def update(self, group_id: UUID, data: ClassGroupUpdate) -> ClassGroupOut:
        group = self.get_or_404(group_id)
        self.terms.get_not_closed(group.term_id)
        if data.name is not None and data.name != group.name and self.repo.get_by_name(group.term_id, data.name):
            raise conflict("Já existe turma com este nome no período")
        self._validate_term_number(group.program.duration_terms, data.curriculum_term_number)
        self._validate_teacher(data.homeroom_teacher_id)
        apply_patch(group, data, clearable=frozenset({"curriculum_term_number", "capacity", "homeroom_teacher_id"}))
        return self.detail(self.repo.save(group).id)

    def delete(self, group_id: UUID) -> None:
        group = self.get_or_404(group_id)
        if group.members:
            raise conflict("Turma possui alunos; remova-os antes")
        if self.repo.has_offerings(group_id):
            raise conflict("Turma possui ofertas vinculadas")
        self.repo.delete(group)

    @staticmethod
    def to_out(group: ClassGroup, member_count: int) -> ClassGroupOut:
        return ClassGroupOut(
            id=group.id,
            program_id=group.program_id,
            term_id=group.term_id,
            name=group.name,
            curriculum_term_number=group.curriculum_term_number,
            shift=group.shift,
            capacity=group.capacity,
            homeroom_teacher_id=group.homeroom_teacher_id,
            member_count=member_count,
        )

    @staticmethod
    def _validate_term_number(duration: int | None, term_number: int | None) -> None:
        if term_number is not None and duration is not None and term_number > duration:
            raise bad_request("Série/semestre além da duração do programa")

    def _validate_teacher(self, teacher_id: UUID | None) -> None:
        if teacher_id is None:
            return
        teacher = self.students.get_by_id(teacher_id)
        if not teacher:
            raise not_found("Professor não encontrado")
        if not has_any_role(teacher, TEACHER_ROLES):
            raise bad_request("Professor responsável precisa ser instrutor, coordenador ou administrador")
