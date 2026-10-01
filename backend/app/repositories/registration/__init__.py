"""Acesso a dados da matricula por disciplina."""

from app.repositories.registration.student_records import StudentRecordRepository
from app.repositories.registration.term_offerings import TermOfferingRepository
from app.repositories.registration.time_slots import OfferingTimeSlotRepository
from app.repositories.registration.windows import RegistrationWindowRepository

__all__ = ["OfferingTimeSlotRepository", "RegistrationWindowRepository", "StudentRecordRepository", "TermOfferingRepository"]
