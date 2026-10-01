from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.schedule import ClassEnrollment, ClassEnrollmentResult, ClassEnrollmentStatus, WaitlistEntry
from app.repositories.registration import StudentRecordRepository, TermOfferingRepository


class SeatAllocator:
    """Grava a vaga ou a posicao na lista de espera (sem validar regras; quem chama ja validou)."""

    def __init__(self, db: Session):
        self.db = db
        self.records = StudentRecordRepository(db)
        self.offerings = TermOfferingRepository(db)

    def enroll(self, offering_id: int, student_id: int) -> ClassEnrollment:
        """Reaproveita a inscricao cancelada antes (uma por aluno e oferta)."""
        enrollment = self.records.enrollment(offering_id, student_id)
        if enrollment is None:
            enrollment = ClassEnrollment(class_offering_id=offering_id, student_id=student_id)
            self.db.add(enrollment)
        enrollment.status = ClassEnrollmentStatus.active
        enrollment.result = ClassEnrollmentResult.in_progress
        enrollment.final_grade = enrollment.recovery_score = enrollment.attendance_rate = None
        return enrollment

    def waitlist(self, offering_id: int, student_id: int) -> WaitlistEntry:
        entry = WaitlistEntry(class_offering_id=offering_id, student_id=student_id, position=self.offerings.next_waitlist_position(offering_id))
        self.db.add(entry)
        return entry

    def waitlist_rank(self, entry: WaitlistEntry) -> int:
        return [e.id for e in self.offerings.waitlist(entry.class_offering_id)].index(entry.id) + 1
