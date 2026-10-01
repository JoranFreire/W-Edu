from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models.schedule import ClassEnrollment, ClassEnrollmentStatus, ClassOffering, ClassStatus, WaitlistEntry
from app.repositories.academic._base import Repository


class TermOfferingRepository(Repository[ClassOffering]):
    """Ofertas de disciplina de um periodo letivo e a ocupacao de cada uma."""

    model = ClassOffering

    def open_for_subjects(self, term_id: int, subject_ids: set[int]) -> list[ClassOffering]:
        if not subject_ids:
            return []
        return (
            self.db.query(ClassOffering)
            .options(joinedload(ClassOffering.instructor))
            .filter(
                ClassOffering.term_id == term_id,
                ClassOffering.subject_id.in_(subject_ids),
                ClassOffering.status == ClassStatus.open,
            )
            .order_by(ClassOffering.name, ClassOffering.id)
            .all()
        )

    def lock(self, offering_id: int) -> ClassOffering | None:
        """Trava a oferta durante a inscricao (duas pessoas disputando a ultima vaga)."""
        return self.db.query(ClassOffering).filter(ClassOffering.id == offering_id).with_for_update().first()

    def seats_taken(self, offering_ids: list[int]) -> dict[int, int]:
        if not offering_ids:
            return {}
        rows = (
            self.db.query(ClassEnrollment.class_offering_id, func.count(ClassEnrollment.id))
            .filter(ClassEnrollment.class_offering_id.in_(offering_ids), ClassEnrollment.status == ClassEnrollmentStatus.active)
            .group_by(ClassEnrollment.class_offering_id)
            .all()
        )
        return dict(rows)

    def waitlist(self, offering_id: int) -> list[WaitlistEntry]:
        return (
            self.db.query(WaitlistEntry)
            .filter(WaitlistEntry.class_offering_id == offering_id)
            .order_by(WaitlistEntry.position, WaitlistEntry.id)
            .all()
        )

    def next_waitlist_position(self, offering_id: int) -> int:
        current = self.db.query(func.max(WaitlistEntry.position)).filter(WaitlistEntry.class_offering_id == offering_id).scalar()
        return (current or 0) + 1
