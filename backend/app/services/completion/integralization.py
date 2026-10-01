from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.completion import FinalProjectStatus
from app.models.student import Student
from app.repositories.academic import ProgramEnrollmentRepository
from app.repositories.completion import ComplementaryActivityRepository, FinalProjectRepository, InternshipRepository
from app.schemas.completion import IntegralizationOut
from app.services.completion.requirements import ProgramTargets, StudentProgress, build_requirements
from app.services.secretariat.lifecycle import EnrollmentLifecycleService
from app.services.secretariat.transcript import TranscriptService


class IntegralizationService:
    """Integralizacao curricular: disciplinas (carga e creditos), atividades complementares, estagio e TCC."""

    def __init__(self, db: Session):
        self.transcripts = TranscriptService(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.enrollments = ProgramEnrollmentRepository(db)
        self.activities = ComplementaryActivityRepository(db)
        self.internships = InternshipRepository(db)
        self.final_projects = FinalProjectRepository(db)

    def for_enrollment(self, enrollment_id: int) -> IntegralizationOut:
        return self.build(self.lifecycle.get_or_404(enrollment_id))

    def for_student(self, student: Student) -> list[IntegralizationOut]:
        return [self.build(enrollment) for enrollment in self.enrollments.list(student_id=student.id)]

    def build(self, enrollment: ProgramEnrollment) -> IntegralizationOut:
        summary = self.transcripts.build(enrollment).summary
        program = enrollment.program
        project = self.final_projects.get_by_enrollment(enrollment.id)
        requirements = build_requirements(
            ProgramTargets(
                mandatory_hours=summary.mandatory_hours, mandatory_credits=summary.mandatory_credits,
                total_hours=program.total_hours, total_credits=program.total_credits,
                complementary_hours=program.complementary_hours, internship_hours=program.internship_hours,
                requires_final_project=program.requires_final_project,
            ),
            StudentProgress(
                mandatory_hours_done=summary.mandatory_hours_done, hours_done=summary.hours_done, credits_done=summary.credits_done,
                complementary_hours_done=self.activities.approved_hours(enrollment.id),
                internship_hours_done=self.internships.approved_mandatory_hours(enrollment.id),
                final_project_approved=project is not None and project.status == FinalProjectStatus.approved,
            ),
        )
        return IntegralizationOut(
            program_enrollment_id=enrollment.id, registration_number=enrollment.registration_number,
            program_name=program.name, cr=summary.cr, requirements=requirements,
            complete=all(requirement.met for requirement in requirements),
        )
