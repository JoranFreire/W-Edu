"""Acesso a dados dos programas sociais: financiadores, beneficios e indicadores da prestacao de contas."""

from app.repositories.social.benefits import BenefitDeliveryRepository, BenefitItemRepository, BenefitStockRepository
from app.repositories.social.funding import FundingSourceRepository
from app.repositories.social.indicators import SocialIndicatorRepository

__all__ = [
    "BenefitDeliveryRepository", "BenefitItemRepository", "BenefitStockRepository", "FundingSourceRepository", "SocialIndicatorRepository",
]
