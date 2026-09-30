from datetime import datetime
from pathlib import Path
import unicodedata

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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
    """PDF de uma pagina (A4) com fonte Helvetica, sem dependencias externas."""
    lines = [
        "CERTIFICADO",
        "Certificamos que",
        student_name,
        "concluiu o curso",
        course_name,
        f"Emitido em {issued_at.strftime('%d/%m/%Y')}",
        f"Codigo de validacao: {validation_code}",
        "Assinado digitalmente por W-Edu",
    ]
    stream_lines = ["BT", "/F1 26 Tf", "72 750 Td", f"({_pdf_text(lines[0])}) Tj", "/F1 13 Tf", "0 -54 Td"]
    for line in lines[1:]:
        stream_lines.append(f"({_pdf_text(line)}) Tj")
        stream_lines.append("0 -32 Td")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    body = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(body)


def _pdf_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return normalized.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
