from __future__ import annotations

from sqlalchemy import or_

from app.core.tenancy import UNSCOPED
from app.models.academic_groups import ProgramEnrollment
from app.models.contracts import EnrollmentContract
from app.models.guardians import StudentGuardian
from app.repositories.academic._base import Repository


class EnrollmentContractRepository(Repository[EnrollmentContract]):
    model = EnrollmentContract

    def list_by_enrollment(self, enrollment_id: int) -> list[EnrollmentContract]:
        return (
            self.db.query(EnrollmentContract)
            .filter(EnrollmentContract.program_enrollment_id == enrollment_id)
            .order_by(EnrollmentContract.created_at.desc(), EnrollmentContract.id.desc())
            .all()
        )

    def list_for_user(self, user_id: int) -> list[EnrollmentContract]:
        """Contratos do aluno e dos dependentes de quem e responsavel financeiro."""
        financial_of = (
            self.db.query(StudentGuardian.student_id)
            .filter(StudentGuardian.guardian_id == user_id, StudentGuardian.is_financial.is_(True))
        )
        return (
            self.db.query(EnrollmentContract)
            .join(ProgramEnrollment, ProgramEnrollment.id == EnrollmentContract.program_enrollment_id)
            .filter(or_(ProgramEnrollment.student_id == user_id, ProgramEnrollment.student_id.in_(financial_of)))
            .order_by(EnrollmentContract.created_at.desc(), EnrollmentContract.id.desc())
            .all()
        )

    def get_by_code_any_institution(self, code: str) -> EnrollmentContract | None:
        # Validacao publica: o codigo e unico na plataforma e a pagina nao tem instituicao ativa.
        return (
            self.db.query(EnrollmentContract)
            .execution_options(**UNSCOPED)
            .filter(EnrollmentContract.validation_code == code)
            .first()
        )
