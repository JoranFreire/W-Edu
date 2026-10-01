from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import joinedload

from app.models.schedule import ClassEnrollment, ClassEnrollmentStatus, ClassOffering
from app.models.student import Student
from app.repositories.academic._base import Repository


class TeachingOfferingRepository(Repository[ClassOffering]):
    """Ofertas vistas pelo docente e suas inscricoes."""

    model = ClassOffering

    def list(self, instructor_id: UUID | None = None) -> list[ClassOffering]:
        query = self.db.query(ClassOffering)
        if instructor_id is not None:
            query = query.filter(ClassOffering.instructor_id == instructor_id)
        return query.order_by(ClassOffering.starts_at.desc()).all()

    def roster(self, offering_id: UUID) -> list[ClassEnrollment]:
        """Alunos da turma: inscricoes ativas ou concluidas (canceladas ficam de fora)."""
        return (
            self.db.query(ClassEnrollment)
            .options(joinedload(ClassEnrollment.student))
            .join(Student, ClassEnrollment.student_id == Student.id)
            .filter(ClassEnrollment.class_offering_id == offering_id, ClassEnrollment.status != ClassEnrollmentStatus.cancelled)
            .order_by(Student.name)
            .all()
        )

    def enrolled_student_ids(self, offering_id: UUID) -> set[UUID]:
        rows = self.db.query(ClassEnrollment.student_id).filter(ClassEnrollment.class_offering_id == offering_id).all()
        return {row[0] for row in rows}
