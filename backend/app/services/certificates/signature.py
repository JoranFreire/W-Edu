from datetime import datetime, timezone
import hashlib
import hmac

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.certificate import Certificate
from app.repositories.certificate import CertificateRepository

ALGORITHM = "HMAC-SHA256"


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
        if not certificate.signature_hash:
            return False
        return hmac.compare_digest(certificate.signature_hash, self._signature_hash(certificate))

    @staticmethod
    def _signature_hash(certificate: Certificate) -> str:
        payload = "|".join([
            str(certificate.id),
            str(certificate.student_id),
            str(certificate.course_id),
            certificate.validation_code,
            certificate.issued_at.isoformat(),
        ])
        return hmac.new(settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
