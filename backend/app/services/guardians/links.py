from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.tenancy import bound_institution_id
from app.models.guardians import StudentGuardian
from app.models.student import Student, UserRole
from app.repositories.guardians import GuardianLinkRepository
from app.repositories.student import StudentRepository
from app.schemas.guardians import GuardianLinkCreate, GuardianLinkUpdate
from app.schemas.student import StudentCreate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.patch import apply_patch
from app.services.membership import MembershipService
from app.services.student import StudentService


class GuardianLinkService:
    """Secretaria vincula responsaveis ao aluno, criando a conta do responsavel quando preciso."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GuardianLinkRepository(db)
        self.users = StudentRepository(db)
        self.students = StudentService(db)
        self.memberships = MembershipService(db)

    def list(self, student_id: int) -> list[StudentGuardian]:
        self._student_or_404(student_id)
        return self.repo.list_by_student(student_id)

    def add(self, student_id: int, data: GuardianLinkCreate) -> StudentGuardian:
        self._student_or_404(student_id)
        guardian = self._guardian_account(data)
        if self.repo.get(student_id, guardian.id):
            raise conflict("Responsável já vinculado a este aluno")
        link = self.repo.add(StudentGuardian(
            student_id=student_id, guardian_id=guardian.id, relationship_kind=data.relationship_kind,
            is_financial=data.is_financial, can_pick_up=data.can_pick_up, is_primary=data.is_primary,
        ))
        self.db.flush()
        if data.is_primary:
            self.repo.clear_primary(student_id, except_id=link.id)
        return self.repo.save(link)

    def update(self, link_id: int, data: GuardianLinkUpdate) -> StudentGuardian:
        link = self._link_or_404(link_id)
        apply_patch(link, data)
        if data.is_primary:
            self.repo.clear_primary(link.student_id, except_id=link.id)
        return self.repo.save(link)

    def remove(self, link_id: int) -> None:
        self.repo.delete(self._link_or_404(link_id))

    def _guardian_account(self, data: GuardianLinkCreate) -> Student:
        """Conta existente (em qualquer instituicao) passa a ser membro desta; senao e criada."""
        existing = self.users.get_by_email(data.email)
        if existing:
            if existing.role != UserRole.guardian:
                raise conflict("E-mail pertence a um usuário que não é responsável")
            self.memberships.add_member(bound_institution_id(self.db), existing)
            return existing
        if not data.password:
            raise bad_request("Informe uma senha inicial para a nova conta do responsável")
        return self.students.create(StudentCreate(name=data.name, email=data.email, password=data.password, role=UserRole.guardian))

    def _student_or_404(self, student_id: int) -> Student:
        student = self.users.get_by_id(student_id)
        if not student or student.role != UserRole.student:
            raise not_found("Aluno não encontrado")
        return student

    def _link_or_404(self, link_id: int) -> StudentGuardian:
        link = self.repo.get_by_id(link_id)
        if not link:
            raise not_found("Vínculo não encontrado")
        return link
