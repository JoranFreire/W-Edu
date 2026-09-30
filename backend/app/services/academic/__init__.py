"""Estrutura curricular (Fase 12): uma area de negocio por modulo."""

from app.services.academic.components import CurriculumComponentService
from app.services.academic.curricula import CurriculumService
from app.services.academic.equivalences import SubjectEquivalenceService
from app.services.academic.prerequisites import SubjectPrerequisiteService
from app.services.academic.programs import ProgramService
from app.services.academic.subjects import SubjectService
from app.services.academic.units import AcademicUnitService

__all__ = [
    "AcademicUnitService",
    "CurriculumComponentService",
    "CurriculumService",
    "ProgramService",
    "SubjectEquivalenceService",
    "SubjectPrerequisiteService",
    "SubjectService",
]
