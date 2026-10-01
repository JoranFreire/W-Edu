from __future__ import annotations

from sqlalchemy.orm import joinedload

from app.models.schedule import ClassEnrollment, ClassEnrollmentResult, ClassEnrollmentStatus, ClassOffering, WaitlistEntry
from app.models.secretariat import CreditTransfer, CreditTransferStatus


class StudentRecordRepository:
    """O que o aluno ja cursou e o que tem no periodo: base dos pre-requisitos e do choque de horario."""

    def __init__(self, db):
        self.db = db

    def approved_subject_ids(self, student_id: int) -> set[int]:
        rows = (
            self.db.query(ClassOffering.subject_id)
            .join(ClassEnrollment, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.result == ClassEnrollmentResult.approved,
                ClassOffering.subject_id.is_not(None),
            )
            .all()
        )
        return {row[0] for row in rows}

    def credited_subject_ids(self, program_enrollment_id: int) -> set[int]:
        rows = (
            self.db.query(CreditTransfer.subject_id)
            .filter(CreditTransfer.program_enrollment_id == program_enrollment_id, CreditTransfer.status == CreditTransferStatus.approved)
            .all()
        )
        return {row[0] for row in rows}

    def term_enrollments(self, student_id: int, term_id: int) -> list[ClassEnrollment]:
        """Inscricoes ativas do aluno em ofertas do periodo."""
        return (
            self.db.query(ClassEnrollment)
            .options(joinedload(ClassEnrollment.class_offering))
            .join(ClassOffering, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.status == ClassEnrollmentStatus.active,
                ClassOffering.term_id == term_id,
            )
            .all()
        )

    def term_waitlist(self, student_id: int, term_id: int) -> list[WaitlistEntry]:
        return (
            self.db.query(WaitlistEntry)
            .join(ClassOffering, WaitlistEntry.class_offering_id == ClassOffering.id)
            .filter(WaitlistEntry.student_id == student_id, ClassOffering.term_id == term_id)
            .all()
        )

    def enrollment(self, offering_id: int, student_id: int) -> ClassEnrollment | None:
        return (
            self.db.query(ClassEnrollment)
            .filter(ClassEnrollment.class_offering_id == offering_id, ClassEnrollment.student_id == student_id)
            .first()
        )

    def waitlist_entry(self, offering_id: int, student_id: int) -> WaitlistEntry | None:
        return (
            self.db.query(WaitlistEntry)
            .filter(WaitlistEntry.class_offering_id == offering_id, WaitlistEntry.student_id == student_id)
            .first()
        )
