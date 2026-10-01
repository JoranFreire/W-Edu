from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.institution import DEFAULT_INSTITUTION_SLUG, Institution, InstitutionStatus
from app.models.student import Student, UserRole
from app.repositories.institution import InstitutionRepository, MembershipRepository
from app.policies.roles import is_super_admin


class TenantAccessService:
    """Escolhe a instituicao ativa de um usuario, valida o acesso e emite o token."""

    def __init__(self, db: Session):
        self.institutions = InstitutionRepository(db)
        self.memberships = MembershipRepository(db)

    def resolve_for_user(self, user: Student, requested: str | int | None = None) -> Institution:
        if requested is not None and requested != "":
            return self._requested(user, requested)
        return self._default_for(user)

    def issue_token(self, user: Student, institution: Institution) -> str:
        return create_access_token(str(user.id), institution.id)

    def _requested(self, user: Student, ref: str | int) -> Institution:
        institution = self.institutions.get_by_ref(ref)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
        if is_super_admin(user):
            return institution
        membership = self.memberships.get(institution.id, user.id)
        if not membership or not membership.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta instituição")
        if institution.status != InstitutionStatus.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instituição inativa")
        return institution

    def _default_for(self, user: Student) -> Institution:
        platform_admin = is_super_admin(user)
        for membership in self.memberships.list_active_for_user(user.id):
            if platform_admin or membership.institution.status == InstitutionStatus.active:
                return membership.institution
        if platform_admin:
            institution = self.institutions.get_by_slug(DEFAULT_INSTITUTION_SLUG) or self.institutions.first()
            if institution:
                return institution
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem instituição ativa")
