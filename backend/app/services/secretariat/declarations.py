from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.pdf import render_text_pdf
from app.core.signing import sign, timestamp, validation_code, verify
from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.secretariat import AcademicDeclaration, DeclarationKind
from app.models.student import Student
from app.repositories.assessment import ClassDiaryRepository, DiaryAttendanceRepository
from app.repositories.institution import InstitutionRepository
from app.repositories.secretariat import DeclarationRepository
from app.schemas.secretariat import DeclarationCreate, DeclarationValidationOut
from app.services.academic.errors import bad_request, conflict, not_found
from app.services.academic.terms import AcademicTermService
from app.services.assessment.attendance_rate import attendance_rate
from app.services.secretariat.declaration_texts import TITLES, DeclarationData, declaration_lines
from app.services.secretariat.lifecycle import EnrollmentLifecycleService


class DeclarationService:
    """Declaracoes de matricula, frequencia e conclusao: emissao, PDF, revogacao e validacao publica."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DeclarationRepository(db)
        self.lifecycle = EnrollmentLifecycleService(db)
        self.terms = AcademicTermService(db)
        self.institutions = InstitutionRepository(db)
        self.diary = ClassDiaryRepository(db)
        self.attendance = DiaryAttendanceRepository(db)

    def list(self, enrollment_id: int) -> list[AcademicDeclaration]:
        self.lifecycle.get_or_404(enrollment_id)
        return self.repo.list_by_enrollment(enrollment_id)

    def list_for_student(self, student: Student) -> list[AcademicDeclaration]:
        return self.repo.list_for_student(student.id)

    def issue(self, enrollment_id: int, data: DeclarationCreate, user_id: int) -> AcademicDeclaration:
        enrollment = self.lifecycle.get_or_404(enrollment_id)
        content = self._content(enrollment, data)
        declaration = self.repo.add(AcademicDeclaration(
            program_enrollment_id=enrollment.id, kind=data.kind, term_id=data.term_id, validation_code=validation_code(),
            title=TITLES[data.kind], lines=declaration_lines(data.kind, content), issued_by_id=user_id,
            issued_at=datetime.now(timezone.utc), signature_hash="",
        ))
        self.db.flush()
        declaration.signature_hash = sign(self._parts(declaration))
        return self.repo.save(declaration)

    def get_or_404(self, declaration_id: int) -> AcademicDeclaration:
        declaration = self.repo.get_by_id(declaration_id)
        if not declaration:
            raise not_found("Declaração não encontrada")
        return declaration

    def get_for_student(self, declaration_id: int, student: Student) -> AcademicDeclaration:
        declaration = self.get_or_404(declaration_id)
        if self.lifecycle.get_or_404(declaration.program_enrollment_id).student_id != student.id:
            raise not_found("Declaração não encontrada")
        return declaration

    def pdf(self, declaration: AcademicDeclaration) -> bytes:
        footer = [f"Codigo de validacao: {declaration.validation_code}", "Assinada digitalmente por W-Edu"]
        if declaration.revoked_at:
            footer.insert(0, "DOCUMENTO REVOGADO")
        return render_text_pdf(declaration.title, [*declaration.lines, "", *footer], title_size=20, body_size=12, leading=24)

    def revoke(self, declaration_id: int, reason: str) -> AcademicDeclaration:
        declaration = self.get_or_404(declaration_id)
        if declaration.revoked_at:
            raise conflict("Declaração já revogada")
        declaration.revoked_at, declaration.revoked_reason = datetime.now(timezone.utc), reason
        return self.repo.save(declaration)

    def validate(self, code: str) -> DeclarationValidationOut:
        declaration = self.repo.get_by_code_any_institution(code)
        if not declaration:
            return DeclarationValidationOut(valid=False, message="Código não encontrado")
        if not verify(declaration.signature_hash, self._parts(declaration)):
            return DeclarationValidationOut(valid=False, message="Assinatura inválida: documento adulterado")
        enrollment = self.db.get(ProgramEnrollment, declaration.program_enrollment_id)
        institution = self.institutions.get_by_id(declaration.institution_id)
        info = {
            "kind": declaration.kind, "title": declaration.title, "issued_at": declaration.issued_at,
            "student_name": enrollment.student.name if enrollment else None, "institution_name": institution.name if institution else None,
        }
        if declaration.revoked_at:
            return DeclarationValidationOut(valid=False, message=f"Declaração revogada: {declaration.revoked_reason}", **info)
        return DeclarationValidationOut(valid=True, message="Declaração válida", **info)

    def _content(self, enrollment: ProgramEnrollment, data: DeclarationCreate) -> DeclarationData:
        institution = self.institutions.get_by_id(enrollment.institution_id)
        base = {
            "institution": institution.name if institution else "A instituicao",
            "student": enrollment.student.name,
            "registration_number": enrollment.registration_number,
            "program": f"{enrollment.program.name} ({enrollment.program.code})",
            "issued_on": date.today(),
        }
        if data.kind == DeclarationKind.enrollment:
            if enrollment.status != ProgramEnrollmentStatus.active:
                raise conflict("Declaração de matrícula exige matrícula ativa")
            term = self.terms.get_or_404(data.term_id).name if data.term_id else None
            return DeclarationData(**base, term=term)
        if data.kind == DeclarationKind.attendance:
            if data.term_id is None:
                raise bad_request("Informe o período letivo da frequência")
            term = self.terms.get_or_404(data.term_id)
            return DeclarationData(**base, term=term.name, attendance=self._attendance(enrollment.student_id, term.id))
        if enrollment.status != ProgramEnrollmentStatus.graduated or not enrollment.concluded_on:
            raise conflict("Declaração de conclusão exige programa concluído")
        return DeclarationData(**base, concluded_on=enrollment.concluded_on, ceremony_on=enrollment.ceremony_on)

    def _attendance(self, student_id: int, term_id: int) -> tuple[tuple[str, float | None], ...]:
        rows = []
        for class_enrollment in self.repo.term_class_enrollments(student_id, term_id):
            rate = class_enrollment.attendance_rate
            if rate is None:
                offering_id = class_enrollment.class_offering_id
                absences = self.attendance.unjustified_absences(offering_id).get(class_enrollment.id, 0)
                rate = attendance_rate(self.diary.total_lessons(offering_id), absences)
            rows.append((class_enrollment.class_offering.name, rate))
        return tuple(rows)

    @staticmethod
    def _parts(declaration: AcademicDeclaration) -> list[str]:
        return [
            str(declaration.id), str(declaration.program_enrollment_id), declaration.kind.value, declaration.validation_code,
            timestamp(declaration.issued_at), "\n".join(declaration.lines),
        ]
