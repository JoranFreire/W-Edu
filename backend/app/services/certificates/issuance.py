from datetime import datetime, timezone
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.notification import NotificationEventType
from app.repositories.certificate import CertificateRepository
from app.repositories.course import CourseRepository
from app.repositories.student import StudentRepository
from app.services.certificates.eligibility import CertificateEligibilityService
from app.services.certificates.pdf import CertificatePdfService
from app.services.certificates.rules import CertificateRuleService
from app.services.certificates.signature import CertificateSigner
from app.services.notification import NotificationService


class CertificateIssuanceService:
    """Emissao (manual ou automatica) e revogacao de certificados."""

    def __init__(self, db: Session):
        self.repo = CertificateRepository(db)
        self.courses = CourseRepository(db)
        self.students = StudentRepository(db)
        self.rules = CertificateRuleService(db)
        self.eligibility = CertificateEligibilityService(db)
        self.signer = CertificateSigner(db)
        self.pdf = CertificatePdfService(db)
        self.notifications = NotificationService(db)

    def issue(self, course_id: int, student_id: int, issued_by_id: int | None = None) -> Certificate:
        evaluation = self.eligibility.evaluate(course_id, student_id)
        if not evaluation.eligible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Aluno não elegível para certificação", "reasons": evaluation.reasons},
            )

        existing = self.repo.get_by_student_and_course(student_id, course_id)
        if existing and existing.revoked_at is None:
            return existing
        certificate = self._reissue(existing, issued_by_id) if existing else self._create(course_id, student_id, issued_by_id)

        course = self.courses.get_by_id(course_id)
        student = self.students.get_by_id(student_id)
        if course and student:
            certificate = self.signer.ensure_signature(certificate)
            self.pdf.ensure_pdf(certificate)
            self.notifications.publish(
                event_type=NotificationEventType.certificate_issued,
                payload={"course_name": course.name, "student_name": student.name, "certificate_code": certificate.validation_code},
                recipient_student_id=student_id,
                course_id=course_id,
            )
        return certificate

    def auto_issue(self, course_id: int, student_id: int) -> Certificate | None:
        """Emite se a regra permitir emissao automatica e o aluno for elegivel; nunca levanta erro."""
        try:
            rule = self.rules.get_rule(course_id)
            if not rule.auto_issue or not self.eligibility.meets_progress(rule, student_id):
                return None
            return self.issue(course_id, student_id)
        except HTTPException:
            return None

    def revoke(self, certificate_id: int, reason: str | None = None) -> Certificate:
        certificate = self.repo.get_by_id(certificate_id)
        if not certificate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado não encontrado")
        certificate.revoked_at = datetime.now(timezone.utc)
        certificate.revoked_reason = reason
        return self.repo.update(certificate)

    def _create(self, course_id: int, student_id: int, issued_by_id: int | None) -> Certificate:
        return self.repo.create(Certificate(
            student_id=student_id,
            course_id=course_id,
            validation_code=_generate_code(),
            issued_by_id=issued_by_id,
        ))

    def _reissue(self, certificate: Certificate, issued_by_id: int | None) -> Certificate:
        """Reemite um certificado revogado com novo codigo."""
        certificate.validation_code = _generate_code()
        certificate.issued_at = datetime.now(timezone.utc)
        certificate.revoked_at = None
        certificate.revoked_reason = None
        certificate.issued_by_id = issued_by_id
        return self.repo.update(certificate)


def _generate_code() -> str:
    return secrets.token_urlsafe(12).replace("-", "").replace("_", "")
