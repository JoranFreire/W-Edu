from __future__ import annotations

from app.models.finance import Charge
from app.models.guardians import StudentGuardian
from app.models.notification import NotificationEvent
from app.repositories.academic._base import Repository


class GuardianLinkRepository(Repository[StudentGuardian]):
    model = StudentGuardian

    def list_by_student(self, student_id: int) -> list[StudentGuardian]:
        return (
            self.db.query(StudentGuardian)
            .filter(StudentGuardian.student_id == student_id)
            .order_by(StudentGuardian.is_primary.desc(), StudentGuardian.id)
            .all()
        )

    def list_by_guardian(self, guardian_id: int) -> list[StudentGuardian]:
        return self.db.query(StudentGuardian).filter(StudentGuardian.guardian_id == guardian_id).order_by(StudentGuardian.id).all()

    def get(self, student_id: int, guardian_id: int) -> StudentGuardian | None:
        return (
            self.db.query(StudentGuardian)
            .filter(StudentGuardian.student_id == student_id, StudentGuardian.guardian_id == guardian_id)
            .first()
        )

    def clear_primary(self, student_id: int, except_id: int | None = None) -> None:
        for link in self.list_by_student(student_id):
            if link.id != except_id:
                link.is_primary = False

    def charges_for(self, student_id: int) -> list[Charge]:
        return self.db.query(Charge).filter(Charge.student_id == student_id).order_by(Charge.id.desc()).all()

    def notices_for(self, student_id: int, limit: int = 50) -> list[NotificationEvent]:
        return (
            self.db.query(NotificationEvent)
            .filter(NotificationEvent.recipient_student_id == student_id)
            .order_by(NotificationEvent.id.desc())
            .limit(limit)
            .all()
        )
