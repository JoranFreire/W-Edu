from __future__ import annotations

from sqlalchemy.orm import joinedload

from app.models.schedule import ClassEnrollment, ClassEnrollmentStatus


class RetentionEnrollmentRepository:
    """Inscricoes da turma acompanhadas no controle de evasao (ativas e desligadas)."""

    def __init__(self, db):
        self.db = db

    def tracked(self, offering_id: int) -> list[ClassEnrollment]:
        return (
            self.db.query(ClassEnrollment)
            .options(joinedload(ClassEnrollment.student))
            .filter(
                ClassEnrollment.class_offering_id == offering_id,
                (ClassEnrollment.status == ClassEnrollmentStatus.active) | ClassEnrollment.dismissed_at.is_not(None),
            )
            .order_by(ClassEnrollment.id)
            .all()
        )

    def get(self, enrollment_id: int) -> ClassEnrollment | None:
        return self.db.get(ClassEnrollment, enrollment_id)
