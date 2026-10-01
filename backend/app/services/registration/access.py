from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.course_registration import RegistrationWindow
from app.models.student import Student
from app.repositories.academic import ProgramEnrollmentRepository
from app.repositories.registration import RegistrationWindowRepository
from app.schemas.course_registration import MyRegistrationWindowOut
from app.services.academic.errors import not_found
from app.services.registration.windows import RegistrationWindowService, to_out


class StudentWindowAccess:
    """Janelas abertas para o aluno e a matricula no programa que cada uma atende."""

    def __init__(self, db: Session):
        self.windows = RegistrationWindowService(db)
        self.window_repo = RegistrationWindowRepository(db)
        self.enrollments = ProgramEnrollmentRepository(db)

    def open_windows(self, student: Student) -> list[MyRegistrationWindowOut]:
        active = self._active(student)
        result = []
        for window in self.window_repo.open_at(datetime.now(timezone.utc), [e.program_id for e in active]):
            enrollment = self._matching(window, active)
            if enrollment:
                result.append(MyRegistrationWindowOut(
                    window=to_out(window), program_enrollment_id=enrollment.id, program_name=enrollment.program.name,
                ))
        return result

    def resolve(self, student: Student, window_id: UUID) -> tuple[RegistrationWindow, ProgramEnrollment]:
        window = self.windows.get_or_404(window_id)
        enrollment = self._matching(window, self._active(student))
        if not enrollment:
            raise not_found("Você não tem matrícula ativa no programa desta janela")
        return window, enrollment

    def _active(self, student: Student) -> list[ProgramEnrollment]:
        return self.enrollments.list(student_id=student.id, status=ProgramEnrollmentStatus.active)

    @staticmethod
    def _matching(window: RegistrationWindow, enrollments: list[ProgramEnrollment]) -> ProgramEnrollment | None:
        """Janela de um programa atende a matricula nele; janela geral, a primeira matricula ativa."""
        return next((e for e in enrollments if window.program_id in (None, e.program_id)), None)
