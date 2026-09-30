from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.institution import Institution
from app.repositories.student import StudentRepository
from app.services.institution import InstitutionService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StudentRepository(db)
        self.institutions = InstitutionService(db)

    def login(self, email: str, password: str, institution: str | None = None) -> tuple[str, Institution]:
        student = self.repo.get_by_email(email)
        # Devolve a conexao ao pool antes do bcrypt (~100 ms de CPU); as proximas consultas reabrem.
        self.db.close()
        if not student or not verify_password(password, student.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        if not student.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta inativa")
        active = self.institutions.resolve_for_user(student, institution)
        return self.institutions.issue_token(student, active), active
