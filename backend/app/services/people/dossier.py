from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.guardians import StudentGuardian
from app.models.student import Student, UserRole
from app.policies.permissions import has_permission
from app.policies.user_scope import ensure_can_view_user
from app.repositories.certificate import CertificateRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.guardians.links import GuardianLinkRepository
from app.repositories.people.dossier import DossierRepository
from app.repositories.school_life.occurrences import OccurrenceRepository
from app.schemas.student import StudentOut
from app.schemas.user_dossier import (
    DossierCertificate,
    DossierContact,
    DossierCourse,
    DossierFinance,
    DossierGuardianLink,
    DossierOccurrence,
    DossierOccurrences,
    DossierOffering,
    DossierPerson,
    DossierProgramEnrollment,
    UserDossier,
)
from app.services.student import StudentService

RECENT_OCCURRENCES = 5


def _person(user: Student) -> DossierPerson:
    profile = user.student_profile
    return DossierPerson(id=user.id, name=user.name, email=user.email, phone=profile.phone if profile else None)


def _link(link: StudentGuardian, other: Student) -> DossierGuardianLink:
    return DossierGuardianLink(
        link_id=link.id, person=_person(other), relationship_kind=link.relationship_kind,
        is_financial=link.is_financial, is_primary=link.is_primary, can_pick_up=link.can_pick_up,
    )


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class UserDossierService:
    """Monta o dossie de uma pessoa; cada secao exige a permissao da area de onde os dados vem."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DossierRepository(db)

    def build(self, current: Student, user_id: int) -> UserDossier:
        user = StudentService(self.db).get_or_404(user_id)
        ensure_can_view_user(current, user)
        can_see_family = has_permission(current, "secretariat.access") or has_permission(current, "school_life.access")
        return UserDossier(
            user=StudentOut.model_validate(user),
            organization_name=user.organization.name if user.organization else None,
            contact=self._contact(user),
            guardians=self._guardians(user) if can_see_family else None,
            dependents=self._dependents(user) if can_see_family and user.role == UserRole.guardian else None,
            program_enrollments=self._program_enrollments(user) if self._can_see_academic(current) else None,
            courses=self._courses(user),
            certificates=self._certificates(user),
            finance=self._finance(user) if has_permission(current, "finance.access") else None,
            occurrences=self._occurrences(user) if has_permission(current, "school_life.access") else None,
            teaching=self._teaching(user) if user.role in {UserRole.instructor, UserRole.coordinator} else None,
        )

    @staticmethod
    def _can_see_academic(current: Student) -> bool:
        return has_permission(current, "secretariat.access") or has_permission(current, "academic.manage")

    @staticmethod
    def _contact(user: Student) -> DossierContact:
        profile = user.student_profile
        if not profile:
            return DossierContact()
        return DossierContact(phone=profile.phone, document=profile.document, position=profile.position,
                              department=profile.department, bio=profile.bio)

    def _guardians(self, user: Student) -> list[DossierGuardianLink]:
        return [_link(link, link.guardian) for link in GuardianLinkRepository(self.db).list_by_student(user.id)]

    def _dependents(self, user: Student) -> list[DossierGuardianLink]:
        return [_link(link, link.student) for link in GuardianLinkRepository(self.db).list_by_guardian(user.id)]

    def _program_enrollments(self, user: Student) -> list[DossierProgramEnrollment]:
        return [
            DossierProgramEnrollment(
                id=enrollment.id, program_code=enrollment.program.code, program_name=enrollment.program.name,
                registration_number=enrollment.registration_number, status=enrollment.status,
                enrolled_on=enrollment.enrolled_on, entry_term_name=enrollment.entry_term.name if enrollment.entry_term else None,
            )
            for enrollment in self.repo.program_enrollments_of(user.id)
        ]

    def _courses(self, user: Student) -> list[DossierCourse]:
        return [
            DossierCourse(course_id=enrollment.course_id, course_name=enrollment.course.name, enrolled_at=enrollment.enrolled_at)
            for enrollment in EnrollmentRepository(self.db).list_by_student(user.id)
        ]

    def _certificates(self, user: Student) -> list[DossierCertificate]:
        return [
            DossierCertificate(id=certificate.id, course_name=certificate.course.name, validation_code=certificate.validation_code,
                               issued_at=certificate.issued_at, revoked=certificate.revoked_at is not None)
            for certificate in CertificateRepository(self.db).list_by_student(user.id)
        ]

    def _finance(self, user: Student) -> DossierFinance:
        charges = self.repo.open_charges_of(user.id)
        now = datetime.now(timezone.utc)
        due_dates = sorted(_as_utc(charge.due_at) for charge in charges if charge.due_at)
        return DossierFinance(
            open_count=len(charges),
            overdue_count=sum(1 for due in due_dates if due < now),
            open_cents=sum(charge.amount_cents for charge in charges),
            next_due_at=next((due for due in due_dates if due >= now), None),
        )

    def _occurrences(self, user: Student) -> DossierOccurrences:
        occurrences = OccurrenceRepository(self.db).list_by_student(user.id)
        recent = sorted(occurrences, key=lambda item: item.occurred_on, reverse=True)[:RECENT_OCCURRENCES]
        return DossierOccurrences(
            total=len(occurrences),
            recent=[DossierOccurrence(id=item.id, kind=item.kind, severity=item.severity, description=item.description,
                                      occurred_on=item.occurred_on) for item in recent],
        )

    def _teaching(self, user: Student) -> list[DossierOffering]:
        return [
            DossierOffering(id=offering.id, name=offering.name, course_name=offering.course.name,
                            term_name=offering.term.name if offering.term else None)
            for offering in self.repo.offerings_taught_by(user.id)
        ]
