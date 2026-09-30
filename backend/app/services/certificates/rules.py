from sqlalchemy.orm import Session

from app.models.course import Course, CourseCompletionRule, CourseModality
from app.repositories.certificate import CourseCompletionRuleRepository
from app.schemas.certificate import CertificateRuleUpdate
from app.services.certificates.lookups import get_course_or_404


class CertificateRuleService:
    """Regra de conclusao de cada curso; cria a regra padrao na primeira consulta."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CourseCompletionRuleRepository(db)

    def get_rule(self, course_id: int) -> CourseCompletionRule:
        course = get_course_or_404(self.db, course_id)
        rule = self.repo.get_by_course(course_id)
        if rule:
            return rule
        return self.repo.create(self._default_rule(course))

    def update_rule(self, course_id: int, data: CertificateRuleUpdate) -> CourseCompletionRule:
        rule = self.get_rule(course_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(rule, field, value)
        return self.repo.update(rule)

    @staticmethod
    def _default_rule(course: Course) -> CourseCompletionRule:
        return CourseCompletionRule(
            course_id=course.id,
            require_lessons_complete=True,
            minimum_progress_percent=100,
            require_quiz=True,
            minimum_quiz_score=70,
            require_attendance=course.modality in {CourseModality.in_person, CourseModality.hybrid},
            minimum_attendance_percent=75,
            auto_issue=True,
        )
