"""Acesso a dados da frequencia usada no controle de evasao."""

from app.repositories.retention.attendance import RetentionAttendanceRepository
from app.repositories.retention.enrollments import RetentionEnrollmentRepository

__all__ = ["RetentionAttendanceRepository", "RetentionEnrollmentRepository"]
