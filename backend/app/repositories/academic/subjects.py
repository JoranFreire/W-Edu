from __future__ import annotations
from uuid import UUID

from sqlalchemy import or_

from app.models.academic import CurriculumComponent, Subject
from app.repositories.academic._base import Repository


class SubjectRepository(Repository[Subject]):
    model = Subject

    def list(self, search: str | None = None, active: bool | None = None) -> list[Subject]:
        query = self.db.query(Subject)
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(Subject.name.ilike(pattern), Subject.code.ilike(pattern)))
        if active is not None:
            query = query.filter(Subject.is_active.is_(active))
        return query.order_by(Subject.code).all()

    def get_by_code(self, code: str) -> Subject | None:
        return self.db.query(Subject).filter(Subject.code == code).first()

    def is_in_curriculum(self, subject_id: UUID) -> bool:
        return (
            self.db.query(CurriculumComponent.id).filter(CurriculumComponent.subject_id == subject_id).first()
            is not None
        )
