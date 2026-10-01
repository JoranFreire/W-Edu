from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.academic_groups import ClassGroup, ClassGroupMember, ProgramEnrollment
from app.models.schedule import ClassEnrollment, ClassOffering


class TeachingScopeRepository:
    """Vinculo docente-aluno: ofertas que o instrutor ministra e turmas-grupo que rege ou em que leciona."""

    def __init__(self, db: Session):
        self.db = db

    def teaches_student(self, instructor_id: int, student_id: int) -> bool:
        in_offering = (
            self.db.query(ClassEnrollment.id)
            .join(ClassOffering, ClassOffering.id == ClassEnrollment.class_offering_id)
            .filter(ClassEnrollment.student_id == student_id, ClassOffering.instructor_id == instructor_id)
            .first()
        )
        if in_offering is not None:
            return True
        teaches_group = self.db.query(ClassOffering.id).filter(
            ClassOffering.class_group_id == ClassGroup.id, ClassOffering.instructor_id == instructor_id
        ).exists()
        in_group = (
            self.db.query(ClassGroupMember.id)
            .join(ClassGroup, ClassGroup.id == ClassGroupMember.class_group_id)
            .join(ProgramEnrollment, ProgramEnrollment.id == ClassGroupMember.program_enrollment_id)
            .filter(ProgramEnrollment.student_id == student_id)
            .filter(or_(ClassGroup.homeroom_teacher_id == instructor_id, teaches_group))
            .first()
        )
        return in_group is not None
