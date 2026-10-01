from sqlalchemy.orm import Session

from app.models.guardians import StudentGuardian
from app.models.student import Student
from app.repositories.guardians.links import GuardianLinkRepository
from app.schemas.user_dossier import DossierGuardianLink, DossierPerson


def _person(user: Student) -> DossierPerson:
    profile = user.student_profile
    return DossierPerson(id=user.id, name=user.name, email=user.email, phone=profile.phone if profile else None)


def _link(link: StudentGuardian, other: Student) -> DossierGuardianLink:
    return DossierGuardianLink(
        link_id=link.id, person=_person(other), relationship_kind=link.relationship_kind,
        is_financial=link.is_financial, is_primary=link.is_primary, can_pick_up=link.can_pick_up,
    )


def guardians_of(db: Session, user: Student) -> list[DossierGuardianLink]:
    return [_link(link, link.guardian) for link in GuardianLinkRepository(db).list_by_student(user.id)]


def dependents_of(db: Session, user: Student) -> list[DossierGuardianLink]:
    return [_link(link, link.student) for link in GuardianLinkRepository(db).list_by_guardian(user.id)]
