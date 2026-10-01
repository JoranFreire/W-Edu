from uuid import UUID

from sqlalchemy.orm import Session

from app.models.student import Student, UserRole
from app.policies.permissions import has_permission
from app.policies.user_scope import ensure_can_view_user
from app.repositories.people.dossier import DossierRepository
from app.schemas.student import StudentOut
from app.schemas.user_dossier import DossierContact, UserDossier
from app.services.people.dossier import academic, family, finance, learning, school_life, warehouse
from app.services.student import StudentService
from app.policies.roles import has_any_role, has_role


def _contact(user: Student) -> DossierContact:
    profile = user.student_profile
    if not profile:
        return DossierContact()
    return DossierContact(phone=profile.phone, document=profile.document, position=profile.position,
                          department=profile.department, bio=profile.bio)


def _any(current: Student, *keys: str) -> bool:
    return any(has_permission(current, key) for key in keys)


class UserDossierService:
    """Monta o dossie de uma pessoa; cada secao exige a permissao da area de onde os dados vem."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DossierRepository(db)

    def build(self, current: Student, user_id: UUID) -> UserDossier:
        user = StudentService(self.db).get_or_404(user_id)
        ensure_can_view_user(current, user)
        sees_family = _any(current, "secretariat.access", "school_life.access")
        return UserDossier(
            user=StudentOut.model_validate(user),
            organization_name=user.organization.name if user.organization else None,
            contact=_contact(user),
            guardians=family.guardians_of(self.db, user) if sees_family else None,
            dependents=family.dependents_of(self.db, user) if sees_family and has_role(user, UserRole.guardian) else None,
            program_enrollments=academic.program_enrollments_of(self.repo, user) if _any(current, "secretariat.access", "academic.manage") else None,
            courses=learning.courses_of(self.db, user),
            certificates=learning.certificates_of(self.db, user),
            finance=finance.finance_of(self.repo, user) if has_permission(current, "finance.access") else None,
            occurrences=school_life.occurrences_of(self.db, user) if has_permission(current, "school_life.access") else None,
            benefits=school_life.benefits_of(self.repo, user) if sees_family else None,
            materials=warehouse.material_requests_of(self.repo, user) if _any(current, "warehouse.manage", "warehouse.reports") else None,
            teaching=academic.offerings_taught_by(self.repo, user) if has_any_role(user, {UserRole.instructor, UserRole.coordinator}) else None,
        )
