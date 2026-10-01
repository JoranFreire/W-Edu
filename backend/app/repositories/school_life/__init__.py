"""Acesso a dados da vida escolar."""

from app.repositories.school_life.agenda import AgendaRepository
from app.repositories.school_life.occurrences import OccurrenceRepository
from app.repositories.school_life.teaching_scope import TeachingScopeRepository

__all__ = ["AgendaRepository", "OccurrenceRepository", "TeachingScopeRepository"]
