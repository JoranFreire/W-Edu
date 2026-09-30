from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.institution import DEFAULT_INSTITUTION_SLUG, Institution, InstitutionStatus
from app.models.student import Student, UserRole
from app.repositories.institution import InstitutionRepository
from app.repositories.student import StudentRepository
from app.schemas.institution import InstitutionAdminCreate, InstitutionCreate, InstitutionUpdate
from app.services.membership import MembershipService


class InstitutionService:
    """Cadastro de instituicoes."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InstitutionRepository(db)

    def list_all(self) -> list[Institution]:
        return self.repo.list_all()

    def get_or_404(self, institution_id: int) -> Institution:
        institution = self.repo.get_by_id(institution_id)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
        return institution

    def get_public(self, ref: str | None) -> Institution:
        """Instituicao ativa para rotas publicas (ex.: cadastro); sem referencia, a padrao."""
        institution = self.repo.get_by_ref(ref) if ref else self.repo.get_by_slug(DEFAULT_INSTITUTION_SLUG)
        if not institution or institution.status != InstitutionStatus.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
        return institution

    def create(self, data: InstitutionCreate) -> Institution:
        if self.repo.get_by_slug(data.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug já utilizado")
        if data.admin and StudentRepository(self.db).get_by_email(data.admin.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail do administrador já cadastrado")
        institution = Institution(**data.model_dump(exclude={"admin"}))
        self.db.add(institution)
        self.db.flush()
        if data.admin:
            self._create_admin(institution, data.admin)
        self.db.commit()
        self.db.refresh(institution)
        return institution

    def update(self, institution: Institution, data: InstitutionUpdate) -> Institution:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(institution, field, value)
        return self.repo.update(institution)

    def _create_admin(self, institution: Institution, data: InstitutionAdminCreate) -> Student:
        admin = Student(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=UserRole.institution_admin,
        )
        self.db.add(admin)
        self.db.flush()
        MembershipService(self.db).add_member(institution.id, admin)
        return admin
