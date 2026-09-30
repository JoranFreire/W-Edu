from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.academic import Curriculum, CurriculumStatus
from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.repositories.academic import CurriculumRepository, ProgramEnrollmentRepository
from app.repositories.student import StudentRepository
from app.schemas.academic_groups import ProgramEnrollmentCreate
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.programs import ProgramService
from app.services.academic.registration import registration_number, registration_prefix
from app.services.academic.terms import AcademicTermService
from app.services.academic.transitions import can_change_enrollment

MAX_NUMBER_ATTEMPTS = 3


class ProgramEnrollmentService:
    """Matricula do aluno no programa: numero de matricula, matriz cursada e situacao."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProgramEnrollmentRepository(db)
        self.curricula = CurriculumRepository(db)
        self.students = StudentRepository(db)
        self.programs = ProgramService(db)
        self.terms = AcademicTermService(db)

    def list(
        self,
        program_id: int | None = None,
        status: ProgramEnrollmentStatus | None = None,
        student_id: int | None = None,
    ) -> list[ProgramEnrollment]:
        return self.repo.list(program_id=program_id, status=status, student_id=student_id)

    def get_or_404(self, enrollment_id: int) -> ProgramEnrollment:
        enrollment = self.repo.get_by_id(enrollment_id)
        if not enrollment:
            raise not_found("Matrícula não encontrada")
        return enrollment

    def create(self, data: ProgramEnrollmentCreate) -> ProgramEnrollment:
        if not self.students.get_by_id(data.student_id):
            raise not_found("Aluno não encontrado")
        program = self.programs.get_or_404(data.program_id)
        curriculum = self._curriculum_for(program.id, data.curriculum_id)
        entry_term = self.terms.get_or_404(data.entry_term_id) if data.entry_term_id else None
        if self.repo.get_open(data.student_id, program.id):
            raise conflict("Aluno já possui matrícula ativa ou trancada neste programa")
        if data.registration_number and self.repo.registration_exists(data.registration_number):
            raise conflict("Número de matrícula já utilizado")

        enrolled_on = data.enrolled_on or date.today()
        prefix = registration_prefix((entry_term.starts_on if entry_term else enrolled_on).year, program.code)
        for attempt in range(MAX_NUMBER_ATTEMPTS):
            number = data.registration_number or registration_number(prefix, self.repo.count_with_prefix(prefix) + 1 + attempt)
            enrollment = ProgramEnrollment(
                student_id=data.student_id,
                program_id=program.id,
                curriculum_id=curriculum.id,
                entry_term_id=data.entry_term_id,
                registration_number=number,
                enrolled_on=enrolled_on,
            )
            try:
                with self.db.begin_nested():
                    self.repo.add(enrollment)
                self.repo.commit()
                return self.get_or_404(enrollment.id)
            except IntegrityError:
                # Numero gerado em paralelo por outra requisicao: tenta o proximo.
                if data.registration_number:
                    raise conflict("Número de matrícula já utilizado")
        raise conflict("Não foi possível gerar o número de matrícula; tente novamente")

    def change_status(self, enrollment_id: int, target: ProgramEnrollmentStatus) -> ProgramEnrollment:
        enrollment = self.get_or_404(enrollment_id)
        if not can_change_enrollment(enrollment.status, target):
            raise conflict(f"Transição de {enrollment.status.value} para {target.value} não permitida")
        if target == ProgramEnrollmentStatus.active and self.repo.get_open(enrollment.student_id, enrollment.program_id) not in (None, enrollment):
            raise conflict("Aluno já possui outra matrícula aberta neste programa")
        enrollment.status = target
        enrollment.status_changed_at = datetime.now(timezone.utc)
        return self.repo.save(enrollment)

    def _curriculum_for(self, program_id: int, curriculum_id: int | None) -> Curriculum:
        if curriculum_id is None:
            active = self.curricula.list_active(program_id)
            if not active:
                raise bad_request("Programa sem matriz vigente; informe a matriz")
            return active[0]
        curriculum = self.curricula.get_by_id(curriculum_id)
        if not curriculum or curriculum.program_id != program_id:
            raise not_found("Matriz curricular não encontrada neste programa")
        if curriculum.status == CurriculumStatus.draft:
            raise bad_request("Matriz em rascunho não recebe matrículas")
        return curriculum
