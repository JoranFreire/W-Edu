"""Acesso a dados dos contratos de matricula."""

from app.repositories.contracts.contracts import EnrollmentContractRepository
from app.repositories.contracts.templates import ContractTemplateRepository

__all__ = ["ContractTemplateRepository", "EnrollmentContractRepository"]
