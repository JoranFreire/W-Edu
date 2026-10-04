from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.facial_assertion import InvalidAssertion, load_public_key, verify_assertion
from app.models.institution import Institution
from app.repositories.facial_login import FacialLoginAssertionRepository
from app.repositories.student import StudentRepository
from app.services.tenant_access import TenantAccessService

_REFUSED = "Não foi possível entrar com o rosto. Use a senha."


class FacialLoginService:
    """Troca o assertion do Persona (rosto conferido) pelo token do W-Edu."""

    def __init__(self, db: Session):
        self.db = db
        self.users = StudentRepository(db)
        self.assertions = FacialLoginAssertionRepository(db)
        self.tenant_access = TenantAccessService(db)

    def login(self, token: str) -> tuple[str, Institution]:
        if not settings.PERSONA_ASSERTION_PUBLIC_KEY:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Login facial desativado")
        try:
            assertion = verify_assertion(token, load_public_key(settings.PERSONA_ASSERTION_PUBLIC_KEY))
        except InvalidAssertion:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_REFUSED)

        user = self.users.get_by_id(assertion.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_REFUSED)
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta inativa")
        if not self.assertions.consume(assertion.jti, user.id, assertion.expires_at):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_REFUSED)

        institution = self.tenant_access.resolve_for_user(user, str(assertion.institution_id))
        self.db.commit()
        return self.tenant_access.issue_token(user, institution), institution
