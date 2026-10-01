from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tuition import StudentDiscount
from app.repositories.tuition import StudentDiscountRepository
from app.schemas.tuition import DiscountCreate
from app.services.academic.errors import not_found
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class StudentDiscountService:
    """Bolsas e descontos da matricula; valem nas parcelas geradas dentro da vigencia."""

    def __init__(self, db: Session):
        self.repo = StudentDiscountRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def list(self, enrollment_id: UUID) -> list[StudentDiscount]:
        self.lifecycle.get_or_404(enrollment_id)
        return self.repo.list_by_enrollment(enrollment_id)

    def create(self, enrollment_id: UUID, data: DiscountCreate) -> StudentDiscount:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        return self.repo.save(StudentDiscount(program_enrollment_id=enrollment.id, **data.model_dump()))

    def deactivate(self, discount_id: UUID) -> StudentDiscount:
        discount = self.repo.get_by_id(discount_id)
        if not discount:
            raise not_found("Desconto não encontrado")
        discount.is_active = False
        return self.repo.save(discount)
