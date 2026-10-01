from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.certificate import CertificateRepository
from app.schemas.user_dossier import DossierCertificate, DossierCourse
from app.services.progress import ProgressService


def courses_of(db: Session, user: Student) -> list[DossierCourse]:
    """Cursos com o progresso nas aulas; concluido quando todas as aulas estao feitas."""
    return [
        DossierCourse(
            course_id=summary.course_id, course_name=summary.course_name, total_lessons=summary.total_lessons,
            done_lessons=summary.done_lessons, progress_percent=summary.progress_percent,
            completed=summary.total_lessons > 0 and summary.done_lessons == summary.total_lessons,
            last_activity_at=summary.last_activity_at,
        )
        for summary in ProgressService(db).course_summary(user.id)
    ]


def certificates_of(db: Session, user: Student) -> list[DossierCertificate]:
    return [
        DossierCertificate(id=certificate.id, course_name=certificate.course.name, validation_code=certificate.validation_code,
                           issued_at=certificate.issued_at, revoked=certificate.revoked_at is not None)
        for certificate in CertificateRepository(db).list_by_student(user.id)
    ]
