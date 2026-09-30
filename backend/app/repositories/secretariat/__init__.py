"""Acesso a dados da secretaria academica, um modulo por entidade."""

from app.repositories.secretariat.credit_transfers import CreditTransferRepository
from app.repositories.secretariat.declarations import DeclarationRepository
from app.repositories.secretariat.events import EnrollmentEventRepository
from app.repositories.secretariat.registrations import TermRegistrationRepository
from app.repositories.secretariat.transcript import TranscriptRepository

__all__ = ["CreditTransferRepository", "DeclarationRepository", "EnrollmentEventRepository", "TermRegistrationRepository", "TranscriptRepository"]
