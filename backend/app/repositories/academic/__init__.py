"""Acesso a dados da estrutura curricular, um modulo por entidade."""

from app.repositories.academic.class_groups import ClassGroupMemberRepository, ClassGroupRepository
from app.repositories.academic.curricula import CurriculumComponentRepository, CurriculumRepository
from app.repositories.academic.enrollments import ProgramEnrollmentRepository
from app.repositories.academic.programs import ProgramRepository
from app.repositories.academic.subject_links import SubjectEquivalenceRepository, SubjectPrerequisiteRepository
from app.repositories.academic.subjects import SubjectRepository
from app.repositories.academic.terms import AcademicTermRepository, CalendarEventRepository, GradingPeriodRepository
from app.repositories.academic.units import AcademicUnitRepository

__all__ = [
    "AcademicTermRepository",
    "CalendarEventRepository",
    "ClassGroupMemberRepository",
    "ClassGroupRepository",
    "GradingPeriodRepository",
    "ProgramEnrollmentRepository",
    "AcademicUnitRepository",
    "CurriculumComponentRepository",
    "CurriculumRepository",
    "ProgramRepository",
    "SubjectEquivalenceRepository",
    "SubjectPrerequisiteRepository",
    "SubjectRepository",
]
