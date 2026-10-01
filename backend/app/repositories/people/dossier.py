from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.finance import Charge, ChargeStatus
from app.models.schedule import ClassOffering


class DossierRepository:
    """Consultas do dossie de uma pessoa que nao pertencem a um unico modulo."""

    def __init__(self, db: Session):
        self.db = db

    def program_enrollments_of(self, user_id: int) -> list[ProgramEnrollment]:
        return (
            self.db.query(ProgramEnrollment)
            .filter(ProgramEnrollment.student_id == user_id)
            .order_by(ProgramEnrollment.enrolled_on.desc())
            .all()
        )

    def open_charges_of(self, user_id: int) -> list[Charge]:
        """Cobrancas pendentes em que a pessoa e o aluno ou quem paga (responsavel financeiro)."""
        return (
            self.db.query(Charge)
            .filter(or_(Charge.student_id == user_id, Charge.payer_id == user_id))
            .filter(Charge.status == ChargeStatus.pending)
            .all()
        )

    def offerings_taught_by(self, user_id: int) -> list[ClassOffering]:
        return (
            self.db.query(ClassOffering)
            .filter(ClassOffering.instructor_id == user_id)
            .order_by(ClassOffering.id.desc())
            .all()
        )
