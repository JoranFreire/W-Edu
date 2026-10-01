from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.repositories.certificate import CertificateRepository
from app.services.certificates.lookups import get_course_or_404, get_student_or_404
from app.services.certificates.pdf import CertificatePdfService
from app.services.certificates.signature import CertificateSigner


class CertificateQueryService:
    """Consultas, validacao publica e preparo para download."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CertificateRepository(db)
        self.signer = CertificateSigner(db)
        self.pdf = CertificatePdfService(db)

    def list_by_student(self, student_id: UUID) -> list[Certificate]:
        get_student_or_404(self.db, student_id)
        return self.repo.list_by_student(student_id)

    def list_by_course(self, course_id: UUID) -> list[Certificate]:
        get_course_or_404(self.db, course_id)
        return self.repo.list_by_course(course_id)

    def validate_code(self, code: str) -> tuple[bool, Certificate | None, str]:
        certificate = self.repo.get_by_code(code)
        if not certificate:
            return False, None, "Certificado não encontrado"
        if certificate.revoked_at is not None:
            return False, certificate, "Certificado revogado"
        self.signer.ensure_signature(certificate)
        if not self.signer.verify_signature(certificate):
            return False, certificate, "Assinatura digital inválida"
        return True, certificate, "Certificado válido"

    def get_for_download(self, certificate_id: UUID, current: Student) -> Certificate:
        certificate = self.repo.get_by_id(certificate_id)
        if not certificate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado não encontrado")
        if current.role not in ADMIN_ROLES | {UserRole.coordinator} and certificate.student_id != current.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito ao titular do certificado")
        if certificate.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificado revogado")
        self.signer.ensure_signature(certificate)
        if not self.signer.verify_signature(certificate):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assinatura digital inválida")
        self.pdf.ensure_pdf(certificate)
        return certificate
