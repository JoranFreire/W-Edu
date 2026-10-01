from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.academic_calendar import AcademicTerm
from app.models.academic_groups import ProgramEnrollment
from app.repositories.institution import InstitutionRepository
from app.services.tuition.payer import PayerResolver
from app.repositories.student import StudentRepository

# Campos aceitos no texto do modelo (documentados na tela de modelos).
FIELDS = ("institution_name", "student_name", "registration_number", "program_name", "program_code", "term_name", "payer_name", "date")


class ContractFields:
    """Valores dos campos do modelo para uma matricula (o pagador e o responsavel financeiro, senao o aluno)."""

    def __init__(self, db: Session):
        self.institutions = InstitutionRepository(db)
        self.payers = PayerResolver(db)
        self.users = StudentRepository(db)

    def of(self, enrollment: ProgramEnrollment, term: AcademicTerm | None) -> dict[str, str]:
        institution = self.institutions.get_by_id(enrollment.institution_id)
        payer_id = self.payers.payer_of(enrollment.student_id)
        payer = self.users.get_by_id(payer_id) if payer_id else enrollment.student
        return {
            "institution_name": institution.name if institution else "",
            "student_name": enrollment.student.name,
            "registration_number": enrollment.registration_number,
            "program_name": enrollment.program.name,
            "program_code": enrollment.program.code,
            "term_name": term.name if term else "",
            "payer_name": payer.name if payer else enrollment.student.name,
            "date": date.today().strftime("%d/%m/%Y"),
        }
