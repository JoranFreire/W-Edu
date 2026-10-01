from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_groups import ProgramEnrollment
from app.models.student import Student
from app.repositories.academic import ProgramEnrollmentRepository
from app.repositories.secretariat import CreditTransferRepository, TranscriptRepository
from app.schemas.secretariat import TranscriptOut
from app.services.academic.summary import effective_credits, effective_hours
from app.services.secretariat.lifecycle import EnrollmentLifecycleService
from app.services.secretariat.transcript_rules import Attempt, Component, Credit, build_rows, summarize


class TranscriptService:
    """Historico escolar: matriz do aluno cruzada com o que ele cursou, aproveitou ou tem pendente."""

    def __init__(self, db: Session):
        self.repo = TranscriptRepository(db)
        self.credits = CreditTransferRepository(db)
        self.enrollments = ProgramEnrollmentRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)

    def for_enrollment(self, enrollment_id: int) -> TranscriptOut:
        return self.build(self.lifecycle.get_or_404(enrollment_id))

    def for_student(self, student: Student) -> list[TranscriptOut]:
        return [self.build(enrollment) for enrollment in self.enrollments.list(student_id=student.id)]

    def build(self, enrollment: ProgramEnrollment) -> TranscriptOut:
        curriculum = enrollment.curriculum
        components = [
            Component(c.subject_id, c.subject.code, c.subject.name, c.term_number, c.kind, effective_hours(c), effective_credits(c))
            for c in curriculum.components
        ]
        curriculum_subjects = {component.subject_id for component in components}
        # Disciplina equivalente cursada conta como a disciplina da matriz.
        counts_as = {subject_id: subject_id for subject_id in curriculum_subjects}
        for first, second in self.repo.equivalences(curriculum_subjects):
            if first in curriculum_subjects and second not in counts_as:
                counts_as[second] = first
            if second in curriculum_subjects and first not in counts_as:
                counts_as[first] = second
        attempts = [
            Attempt(
                subject_id=counts_as[e.class_offering.subject_id],
                grade=e.final_grade,
                result=e.result,
                taken_in=e.class_offering.term.name if e.class_offering.term else e.class_offering.name,
            )
            for e in self.repo.attempts(enrollment.student_id, set(counts_as))
        ]
        credits = [
            Credit(t.subject_id, t.grade, t.source_institution or t.source_subject)
            for t in self.credits.approved(enrollment.id)
        ]
        rows = build_rows(components, attempts, credits)
        return TranscriptOut(
            program_enrollment_id=enrollment.id,
            registration_number=enrollment.registration_number,
            student_name=enrollment.student.name,
            program_code=enrollment.program.code,
            program_name=enrollment.program.name,
            curriculum_version=curriculum.version,
            status=enrollment.status.value,
            rows=rows,
            summary=summarize(rows),
        )
