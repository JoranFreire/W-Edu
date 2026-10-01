from __future__ import annotations
from uuid import UUID

from app.core.tenancy import UNSCOPED
from app.models.academic_groups import ProgramEnrollment
from app.models.schedule import ClassEnrollment, ClassOffering
from app.models.secretariat import AcademicDeclaration
from app.repositories.academic._base import Repository


class DeclarationRepository(Repository[AcademicDeclaration]):
    model = AcademicDeclaration

    def list_by_enrollment(self, enrollment_id: UUID) -> list[AcademicDeclaration]:
        return (
            self.db.query(AcademicDeclaration)
            .filter(AcademicDeclaration.program_enrollment_id == enrollment_id)
            .order_by(AcademicDeclaration.issued_at.desc())
            .all()
        )

    def list_for_student(self, student_id: UUID) -> list[AcademicDeclaration]:
        return (
            self.db.query(AcademicDeclaration)
            .join(ProgramEnrollment, AcademicDeclaration.program_enrollment_id == ProgramEnrollment.id)
            .filter(ProgramEnrollment.student_id == student_id)
            .order_by(AcademicDeclaration.issued_at.desc())
            .all()
        )

    def get_by_code_any_institution(self, code: str) -> AcademicDeclaration | None:
        # Validacao publica: o codigo e unico na plataforma e a pagina nao tem instituicao ativa.
        return (
            self.db.query(AcademicDeclaration)
            .execution_options(**UNSCOPED)
            .filter(AcademicDeclaration.validation_code == code)
            .first()
        )

    def term_class_enrollments(self, student_id: UUID, term_id: UUID) -> list[ClassEnrollment]:
        return (
            self.db.query(ClassEnrollment)
            .join(ClassOffering, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(ClassEnrollment.student_id == student_id, ClassOffering.term_id == term_id)
            .order_by(ClassOffering.name)
            .all()
        )
