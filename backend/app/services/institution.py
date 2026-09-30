from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.institution import DEFAULT_INSTITUTION_SLUG, Campus, Institution, InstitutionMembership, InstitutionStatus
from app.models.student import Student, UserRole
from app.repositories.institution import CampusRepository, InstitutionRepository, MembershipRepository
from app.repositories.student import StudentRepository
from app.schemas.institution import CampusCreate, CampusUpdate, InstitutionCreate, InstitutionUpdate


class InstitutionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InstitutionRepository(db)
        self.membership_repo = MembershipRepository(db)
        self.campus_repo = CampusRepository(db)

    def resolve_for_user(self, user: Student, requested: str | int | None = None) -> Institution:
        """Escolhe a instituicao ativa do usuario e valida o acesso a ela."""
        is_super_admin = user.role == UserRole.super_admin
        if requested is not None and requested != "":
            institution = self.repo.get_by_ref(requested)
            if not institution:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
            if not is_super_admin:
                membership = self.membership_repo.get(institution.id, user.id)
                if not membership or not membership.is_active:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta instituição")
                if institution.status != InstitutionStatus.active:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instituição inativa")
            return institution

        for membership in self.membership_repo.list_active_for_user(user.id):
            if is_super_admin or membership.institution.status == InstitutionStatus.active:
                return membership.institution
        if is_super_admin:
            institution = self.repo.get_by_slug(DEFAULT_INSTITUTION_SLUG) or self.repo.first()
            if institution:
                return institution
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem instituição ativa")

    def issue_token(self, user: Student, institution: Institution) -> str:
        return create_access_token(str(user.id), institution.id)

    def list_memberships(self, user: Student) -> list[InstitutionMembership]:
        return self.membership_repo.list_active_for_user(user.id)

    def get_or_404(self, institution_id: int) -> Institution:
        institution = self.repo.get_by_id(institution_id)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
        return institution

    def get_public(self, ref: str | None) -> Institution:
        institution = self.repo.get_by_ref(ref) if ref else self.repo.get_by_slug(DEFAULT_INSTITUTION_SLUG)
        if not institution or institution.status != InstitutionStatus.active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
        return institution

    def list_all(self) -> list[Institution]:
        return self.repo.list_all()

    def create(self, data: InstitutionCreate) -> Institution:
        if self.repo.get_by_slug(data.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug já utilizado")
        admin_data = data.admin
        if admin_data and StudentRepository(self.db).get_by_email(admin_data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail do administrador já cadastrado")
        institution = Institution(**data.model_dump(exclude={"admin"}))
        self.db.add(institution)
        self.db.flush()
        if admin_data:
            admin = Student(
                name=admin_data.name,
                email=admin_data.email,
                password_hash=hash_password(admin_data.password),
                role=UserRole.institution_admin,
            )
            self.db.add(admin)
            self.db.flush()
            self.add_member(institution.id, admin)
        self.db.commit()
        self.db.refresh(institution)
        return institution

    def update(self, institution: Institution, data: InstitutionUpdate) -> Institution:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(institution, field, value)
        return self.repo.update(institution)

    def add_member(self, institution_id: int, user: Student) -> InstitutionMembership:
        membership = self.membership_repo.get(institution_id, user.id)
        if membership:
            membership.role = user.role
            membership.is_active = True
            return membership
        return self.membership_repo.add(InstitutionMembership(institution_id=institution_id, user_id=user.id, role=user.role))

    def sync_member_role(self, institution_id: int, user: Student) -> None:
        membership = self.membership_repo.get(institution_id, user.id)
        if membership:
            membership.role = user.role
            membership.is_active = user.is_active

    def list_campuses(self, institution_id: int | None = None) -> list[Campus]:
        if institution_id is not None:
            return self.campus_repo.list_by_institution(institution_id)
        return self.campus_repo.list_all()

    def get_campus_or_404(self, campus_id: int) -> Campus:
        campus = self.campus_repo.get_by_id(campus_id)
        if not campus:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campus não encontrado")
        return campus

    def create_campus(self, data: CampusCreate) -> Campus:
        return self.campus_repo.create(Campus(**data.model_dump()))

    def update_campus(self, campus_id: int, data: CampusUpdate) -> Campus:
        campus = self.get_campus_or_404(campus_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(campus, field, value)
        return self.campus_repo.update(campus)

    def delete_campus(self, campus_id: int) -> None:
        campus = self.get_campus_or_404(campus_id)
        if campus.locations:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Campus possui locais vinculados")
        self.campus_repo.delete(campus)
