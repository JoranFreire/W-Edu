"""Acesso a dados das mensalidades."""

from app.repositories.tuition.charges import TuitionChargeRepository
from app.repositories.tuition.discounts import StudentDiscountRepository
from app.repositories.tuition.plans import TuitionPlanRepository

__all__ = ["StudentDiscountRepository", "TuitionChargeRepository", "TuitionPlanRepository"]
