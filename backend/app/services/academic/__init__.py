"""Estrutura curricular (Fase 12): uma area de negocio por modulo."""

from app.services.academic.calendar_events import CalendarEventService
from app.services.academic.class_group_members import ClassGroupMemberService
from app.services.academic.class_groups import ClassGroupService
from app.services.academic.components import CurriculumComponentService
from app.services.academic.curricula import CurriculumService
from app.services.academic.equivalences import SubjectEquivalenceService
from app.services.academic.grading_periods import GradingPeriodService
from app.services.academic.program_enrollments import ProgramEnrollmentService
from app.services.academic.prerequisites import SubjectPrerequisiteService
from app.services.academic.programs import ProgramService
from app.services.academic.subjects import SubjectService
from app.services.academic.terms import AcademicTermService
from app.services.academic.units import AcademicUnitService

__all__ = [
    "AcademicTermService",
    "CalendarEventService",
    "ClassGroupMemberService",
    "ClassGroupService",
    "GradingPeriodService",
    "ProgramEnrollmentService",
    "AcademicUnitService",
    "CurriculumComponentService",
    "CurriculumService",
    "ProgramService",
    "SubjectEquivalenceService",
    "SubjectPrerequisiteService",
    "SubjectService",
]
