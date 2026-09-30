"""Acesso a dados de avaliacao e diario, um modulo por entidade."""

from app.repositories.assessment.diary import ClassDiaryRepository, DiaryAttendanceRepository
from app.repositories.assessment.grades import GradeEntryRepository
from app.repositories.assessment.items import AssessmentItemRepository
from app.repositories.assessment.offerings import TeachingOfferingRepository
from app.repositories.assessment.results import PeriodClosureRepository, PeriodResultRepository, StudentEnrollmentRepository
from app.repositories.assessment.schemes import GradingSchemeRepository

__all__ = [
    "AssessmentItemRepository",
    "ClassDiaryRepository",
    "DiaryAttendanceRepository",
    "GradeEntryRepository",
    "GradingSchemeRepository",
    "PeriodClosureRepository",
    "PeriodResultRepository",
    "StudentEnrollmentRepository",
    "TeachingOfferingRepository",
]
