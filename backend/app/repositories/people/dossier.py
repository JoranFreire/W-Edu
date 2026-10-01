from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.academic_groups import ProgramEnrollment
from app.models.finance import Charge
from app.models.schedule import ClassOffering
from app.models.social_programs import BenefitDelivery
from app.models.warehouse import MaterialRequest, MaterialRequestLine


class DossierRepository:
    """Consultas do dossie de uma pessoa que nao pertencem a um unico modulo."""

    def __init__(self, db: Session):
        self.db = db

    def program_enrollments_of(self, user_id: UUID) -> list[ProgramEnrollment]:
        return (
            self.db.query(ProgramEnrollment)
            .filter(ProgramEnrollment.student_id == user_id)
            .order_by(ProgramEnrollment.enrolled_on.desc())
            .all()
        )

    def charges_of(self, user_id: UUID) -> list[Charge]:
        """Cobrancas em que a pessoa e o aluno ou quem paga (responsavel financeiro), mais recentes primeiro."""
        return (
            self.db.query(Charge)
            .filter(or_(Charge.student_id == user_id, Charge.payer_id == user_id))
            .order_by(Charge.due_at.desc().nullslast(), Charge.id.desc())
            .all()
        )

    def offerings_taught_by(self, user_id: UUID) -> list[ClassOffering]:
        return (
            self.db.query(ClassOffering)
            .filter(ClassOffering.instructor_id == user_id)
            .order_by(ClassOffering.id.desc())
            .all()
        )

    def benefits_of(self, user_id: UUID) -> list[tuple[BenefitDelivery, str]]:
        """Entregas de beneficios ao aluno, com o nome da turma."""
        return (
            self.db.query(BenefitDelivery, ClassOffering.name)
            .join(ClassOffering, ClassOffering.id == BenefitDelivery.class_offering_id)
            .options(selectinload(BenefitDelivery.item))
            .filter(BenefitDelivery.student_id == user_id)
            .order_by(BenefitDelivery.delivered_on.desc(), BenefitDelivery.id.desc())
            .all()
        )

    def material_requests_of(self, user_id: UUID) -> list[MaterialRequest]:
        return (
            self.db.query(MaterialRequest)
            .options(selectinload(MaterialRequest.lines).selectinload(MaterialRequestLine.item),
                     selectinload(MaterialRequest.class_offering))
            .filter(MaterialRequest.requester_id == user_id)
            .order_by(MaterialRequest.needed_on.desc(), MaterialRequest.id.desc())
            .all()
        )
