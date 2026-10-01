from app.models.student import Student
from app.repositories.people.dossier import DossierRepository
from app.schemas.user_dossier import DossierOffering, DossierProgramEnrollment


def program_enrollments_of(repo: DossierRepository, user: Student) -> list[DossierProgramEnrollment]:
    return [
        DossierProgramEnrollment(
            id=enrollment.id, program_code=enrollment.program.code, program_name=enrollment.program.name,
            registration_number=enrollment.registration_number, status=enrollment.status, enrolled_on=enrollment.enrolled_on,
            entry_term_name=enrollment.entry_term.name if enrollment.entry_term else None,
        )
        for enrollment in repo.program_enrollments_of(user.id)
    ]


def offerings_taught_by(repo: DossierRepository, user: Student) -> list[DossierOffering]:
    return [
        DossierOffering(id=offering.id, name=offering.name, course_name=offering.course.name,
                        term_name=offering.term.name if offering.term else None)
        for offering in repo.offerings_taught_by(user.id)
    ]
