"""Acesso a dados do processo seletivo."""

from app.repositories.admissions.applications import AdmissionApplicationRepository, ApplicationDocumentRepository
from app.repositories.admissions.calls import AdmissionCallRepository

__all__ = ["AdmissionApplicationRepository", "AdmissionCallRepository", "ApplicationDocumentRepository"]
