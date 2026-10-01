from __future__ import annotations
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models.academic_groups import ClassGroup, ClassGroupMember, ProgramEnrollment
from app.models.schedule import ClassOffering
from app.repositories.academic._base import Repository


class ClassGroupRepository(Repository[ClassGroup]):
    model = ClassGroup

    def list(self, term_id: UUID | None = None, program_id: UUID | None = None) -> list[ClassGroup]:
        query = self.db.query(ClassGroup)
        if term_id is not None:
            query = query.filter(ClassGroup.term_id == term_id)
        if program_id is not None:
            query = query.filter(ClassGroup.program_id == program_id)
        return query.order_by(ClassGroup.name).all()

    def get_by_name(self, term_id: UUID, name: str) -> ClassGroup | None:
        return self.db.query(ClassGroup).filter(ClassGroup.term_id == term_id, ClassGroup.name == name).first()

    def member_counts(self, group_ids: list[UUID]) -> dict[UUID, int]:
        if not group_ids:
            return {}
        rows = (
            self.db.query(ClassGroupMember.class_group_id, func.count(ClassGroupMember.id))
            .filter(ClassGroupMember.class_group_id.in_(group_ids))
            .group_by(ClassGroupMember.class_group_id)
            .all()
        )
        return dict(rows)

    def has_offerings(self, group_id: UUID) -> bool:
        return self.db.query(ClassOffering.id).filter(ClassOffering.class_group_id == group_id).first() is not None

    def taught_by(self, group_id: UUID, instructor_id: UUID) -> bool:
        """O instrutor ministra alguma oferta ligada a turma-grupo."""
        return (
            self.db.query(ClassOffering.id)
            .filter(ClassOffering.class_group_id == group_id, ClassOffering.instructor_id == instructor_id)
            .first()
            is not None
        )


class ClassGroupMemberRepository(Repository[ClassGroupMember]):
    model = ClassGroupMember

    def list_by_group(self, group_id: UUID) -> list[ClassGroupMember]:
        return (
            self.db.query(ClassGroupMember)
            .options(joinedload(ClassGroupMember.program_enrollment).joinedload(ProgramEnrollment.student))
            .join(ProgramEnrollment, ClassGroupMember.program_enrollment_id == ProgramEnrollment.id)
            .filter(ClassGroupMember.class_group_id == group_id)
            .order_by(ProgramEnrollment.registration_number)
            .all()
        )

    def count(self, group_id: UUID) -> int:
        return self.db.query(ClassGroupMember.id).filter(ClassGroupMember.class_group_id == group_id).count()

    def get(self, group_id: UUID, enrollment_id: UUID) -> ClassGroupMember | None:
        return (
            self.db.query(ClassGroupMember)
            .filter(ClassGroupMember.class_group_id == group_id, ClassGroupMember.program_enrollment_id == enrollment_id)
            .first()
        )

    def group_in_term(self, enrollment_id: UUID, term_id: UUID) -> ClassGroup | None:
        """Turma-grupo em que a matricula ja esta alocada no periodo."""
        return (
            self.db.query(ClassGroup)
            .join(ClassGroupMember, ClassGroupMember.class_group_id == ClassGroup.id)
            .filter(ClassGroupMember.program_enrollment_id == enrollment_id, ClassGroup.term_id == term_id)
            .first()
        )

    def groups_of_student(self, student_id: UUID) -> list[ClassGroup]:
        """Turmas-grupo em que o aluno esta alocado (por qualquer matricula no curso)."""
        return (
            self.db.query(ClassGroup)
            .join(ClassGroupMember, ClassGroupMember.class_group_id == ClassGroup.id)
            .join(ProgramEnrollment, ProgramEnrollment.id == ClassGroupMember.program_enrollment_id)
            .filter(ProgramEnrollment.student_id == student_id)
            .order_by(ClassGroup.id)
            .all()
        )

    def student_ids(self, group_id: UUID) -> list[UUID]:
        rows = (
            self.db.query(ProgramEnrollment.student_id)
            .join(ClassGroupMember, ClassGroupMember.program_enrollment_id == ProgramEnrollment.id)
            .filter(ClassGroupMember.class_group_id == group_id)
            .distinct()
            .all()
        )
        return [row[0] for row in rows]
