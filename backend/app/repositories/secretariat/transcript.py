from __future__ import annotations
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.academic import SubjectEquivalence
from app.models.schedule import ClassEnrollment, ClassEnrollmentStatus, ClassOffering


class TranscriptRepository:
    """Consultas do historico escolar: disciplinas cursadas pelo aluno e equivalencias."""

    def __init__(self, db: Session):
        self.db = db

    def attempts(self, student_id: UUID, subject_ids: set[UUID]) -> list[ClassEnrollment]:
        if not subject_ids:
            return []
        return (
            self.db.query(ClassEnrollment)
            .options(joinedload(ClassEnrollment.class_offering).joinedload(ClassOffering.term))
            .join(ClassOffering, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.status != ClassEnrollmentStatus.cancelled,
                ClassOffering.subject_id.in_(subject_ids),
            )
            .order_by(ClassOffering.starts_at)
            .all()
        )

    def equivalences(self, subject_ids: set[UUID]) -> list[tuple[int, int]]:
        if not subject_ids:
            return []
        rows = (
            self.db.query(SubjectEquivalence.subject_id, SubjectEquivalence.equivalent_subject_id)
            .filter(or_(SubjectEquivalence.subject_id.in_(subject_ids), SubjectEquivalence.equivalent_subject_id.in_(subject_ids)))
            .all()
        )
        return [(a, b) for a, b in rows]
