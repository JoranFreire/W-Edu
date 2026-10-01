"""Acesso a dados dos requisitos de conclusao: atividades complementares, estagios e TCC."""

from app.repositories.completion.activities import ComplementaryActivityRepository
from app.repositories.completion.final_projects import FinalProjectRepository
from app.repositories.completion.internships import InternshipLogRepository, InternshipRepository

__all__ = ["ComplementaryActivityRepository", "FinalProjectRepository", "InternshipLogRepository", "InternshipRepository"]
