from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.pdf import render_text_pdf
from app.core.storage import certificates_storage_dir
from app.models.certificate import Certificate
from app.repositories.certificate import CertificateRepository
from app.repositories.course import CourseRepository
from app.repositories.student import StudentRepository


class CertificatePdfService:
    """Gera e guarda o PDF do certificado quando ainda nao existe em disco."""

    def __init__(self, db: Session):
        self.repo = CertificateRepository(db)
        self.courses = CourseRepository(db)
        self.students = StudentRepository(db)

    def ensure_pdf(self, certificate: Certificate) -> Certificate:
        if certificate.pdf_url and Path(certificate.pdf_url).exists():
            return certificate
        course = certificate.course or self.courses.get_by_id(certificate.course_id)
        student = certificate.student or self.students.get_by_id(certificate.student_id)
        if not course or not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dados do certificado incompletos")

        target = certificates_storage_dir() / f"certificate_{certificate.id}_{certificate.validation_code}.pdf"
        target.write_bytes(render_certificate_pdf(
            student_name=student.name,
            course_name=course.name,
            issued_at=certificate.issued_at,
            validation_code=certificate.validation_code,
        ))
        certificate.pdf_url = str(target)
        return self.repo.update(certificate)


def render_certificate_pdf(*, student_name: str, course_name: str, issued_at: datetime, validation_code: str) -> bytes:
    return render_text_pdf("CERTIFICADO", [
        "Certificamos que",
        student_name,
        "concluiu o curso",
        course_name,
        f"Emitido em {issued_at.strftime('%d/%m/%Y')}",
        f"Codigo de validacao: {validation_code}",
        "Assinado digitalmente por W-Edu",
    ])
