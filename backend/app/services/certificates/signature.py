from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.signing import ALGORITHM, sign, verify
from app.models.certificate import Certificate
from app.repositories.certificate import CertificateRepository


class CertificateSigner:
    """Assinatura de integridade (HMAC) dos dados do certificado."""

    def __init__(self, db: Session):
        self.repo = CertificateRepository(db)

    def ensure_signature(self, certificate: Certificate) -> Certificate:
        """Assina certificados ainda sem assinatura; assinaturas existentes nunca sao sobrescritas."""
        if certificate.signature_hash or certificate.signature_algorithm:
            return certificate
        certificate.signature_algorithm = ALGORITHM
        certificate.signature_hash = self._signature_hash(certificate)
        certificate.signed_at = datetime.now(timezone.utc)
        return self.repo.update(certificate)

    def verify_signature(self, certificate: Certificate) -> bool:
        return verify(certificate.signature_hash, self._parts(certificate))

    def _signature_hash(self, certificate: Certificate) -> str:
        return sign(self._parts(certificate))

    @staticmethod
    def _parts(certificate: Certificate) -> list[str]:
        return [
            str(certificate.id),
            str(certificate.student_id),
            str(certificate.course_id),
            certificate.validation_code,
            certificate.issued_at.isoformat(),
        ]
