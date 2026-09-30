from sqlalchemy.orm import Session, selectinload

from app.models.assignment import AssignmentSubmission, AssignmentSubmissionStatus
from app.models.course import CourseCompletionRule
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson, LessonType
from app.models.progress import Progress, ProgressStatus
from app.models.quiz import QuizAttempt
from app.models.schedule import (
    AttendanceRecord,
    AttendanceStatus,
    ClassEnrollment,
    ClassEnrollmentStatus,
    ClassOffering,
    PracticalAssessmentRecord,
    PracticalAssessmentStatus,
    ScheduledMeeting,
)
from app.schemas.certificate import CertificateEligibilityOut
from app.services.certificates.lookups import get_course_or_404, get_student_or_404
from app.services.certificates.rules import CertificateRuleService


class CertificateEligibilityService:
    """Calcula progresso, desempenho e frequencia do aluno frente a regra do curso."""

    def __init__(self, db: Session):
        self.db = db
        self.rules = CertificateRuleService(db)

    def evaluate(self, course_id: int, student_id: int) -> CertificateEligibilityOut:
        get_course_or_404(self.db, course_id)
        get_student_or_404(self.db, student_id)
        rule = self.rules.get_rule(course_id)
        reasons: list[str] = []

        if not self._is_enrolled(course_id, student_id):
            reasons.append("Aluno não está matriculado no curso")

        lessons = self._lessons_with_quiz(course_id)
        progress_percent = self.progress_percent(student_id, lessons)
        if rule.require_lessons_complete and progress_percent < rule.minimum_progress_percent:
            reasons.append("Progresso insuficiente")

        quiz_percent = self._quiz_percent(student_id, lessons, rule.minimum_quiz_score)
        if rule.require_quiz and quiz_percent < rule.minimum_quiz_score:
            reasons.append("Desempenho em avaliações insuficiente")

        attendance_percent = self._attendance_percent(student_id, course_id)
        if rule.require_attendance and attendance_percent < rule.minimum_attendance_percent:
            reasons.append("Frequência insuficiente")

        return CertificateEligibilityOut(
            course_id=course_id,
            student_id=student_id,
            eligible=not reasons,
            progress_percent=progress_percent,
            quiz_percent=quiz_percent,
            attendance_percent=attendance_percent,
            reasons=reasons,
        )

    def meets_progress(self, rule: CourseCompletionRule, student_id: int) -> bool:
        """Verificacao barata usada antes da avaliacao completa na emissao automatica."""
        if not rule.require_lessons_complete:
            return True
        lessons = self.db.query(Lesson).filter(Lesson.course_id == rule.course_id).all()
        return self.progress_percent(student_id, lessons) >= rule.minimum_progress_percent

    def progress_percent(self, student_id: int, lessons: list[Lesson]) -> int:
        if not lessons:
            return 100
        lesson_ids = {lesson.id for lesson in lessons}
        records = self.db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.lesson_id.in_(lesson_ids),
        ).all()
        done = sum(1 for record in records if record.status == ProgressStatus.done)
        return round(done / len(lessons) * 100)

    def _is_enrolled(self, course_id: int, student_id: int) -> bool:
        return self.db.query(Enrollment).filter(
            Enrollment.course_id == course_id,
            Enrollment.student_id == student_id,
        ).first() is not None

    def _lessons_with_quiz(self, course_id: int) -> list[Lesson]:
        return (
            self.db.query(Lesson)
            .options(selectinload(Lesson.quiz))
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.order)
            .all()
        )

    def _quiz_percent(self, student_id: int, lessons: list[Lesson], minimum_score: int) -> int:
        assessment_lessons = [lesson for lesson in lessons if lesson.quiz is not None or lesson.type == LessonType.assessment]
        if not assessment_lessons:
            return 100
        passed = sum(1 for lesson in assessment_lessons if self._passed_assessment(student_id, lesson, minimum_score))
        return round(passed / len(assessment_lessons) * 100)

    def _passed_assessment(self, student_id: int, lesson: Lesson, minimum_score: int) -> bool:
        """Aprovado se passou no quiz, na entrega corrigida ou na avaliacao pratica da aula."""
        if lesson.quiz and self._passed_quiz(student_id, lesson.quiz.id):
            return True
        if lesson.type != LessonType.assessment:
            return False
        return self._passed_submission(student_id, lesson.id, minimum_score) or self._passed_practical(student_id, lesson.id, minimum_score)

    def _passed_quiz(self, student_id: int, quiz_id: int) -> bool:
        best_attempt = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.student_id == student_id, QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.score.desc(), QuizAttempt.attempted_at.desc())
            .first()
        )
        return bool(best_attempt and best_attempt.passed)

    def _passed_submission(self, student_id: int, lesson_id: int, minimum_score: int) -> bool:
        submission = (
            self.db.query(AssignmentSubmission)
            .filter(
                AssignmentSubmission.lesson_id == lesson_id,
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.status == AssignmentSubmissionStatus.reviewed,
            )
            .order_by(AssignmentSubmission.reviewed_at.desc().nullslast(), AssignmentSubmission.submitted_at.desc())
            .first()
        )
        return bool(submission and submission.score is not None and submission.score >= minimum_score)

    def _passed_practical(self, student_id: int, lesson_id: int, minimum_score: int) -> bool:
        practical = (
            self.db.query(PracticalAssessmentRecord)
            .join(ScheduledMeeting, ScheduledMeeting.id == PracticalAssessmentRecord.scheduled_meeting_id)
            .filter(
                ScheduledMeeting.lesson_id == lesson_id,
                PracticalAssessmentRecord.student_id == student_id,
                PracticalAssessmentRecord.status == PracticalAssessmentStatus.reviewed,
            )
            .order_by(PracticalAssessmentRecord.score.desc(), PracticalAssessmentRecord.recorded_at.desc())
            .first()
        )
        return bool(practical and practical.score >= minimum_score)

    def _attendance_percent(self, student_id: int, course_id: int) -> int:
        class_offering_ids = [
            row[0]
            for row in self.db.query(ClassOffering.id)
            .join(ClassEnrollment, ClassEnrollment.class_offering_id == ClassOffering.id)
            .filter(
                ClassOffering.course_id == course_id,
                ClassEnrollment.student_id == student_id,
                ClassEnrollment.status == ClassEnrollmentStatus.active,
            )
            .distinct()
            .all()
        ]
        if not class_offering_ids:
            return 0

        meeting_ids = [
            row[0]
            for row in self.db.query(ScheduledMeeting.id)
            .filter(
                ScheduledMeeting.class_offering_id.in_(class_offering_ids),
                ScheduledMeeting.is_closed.is_(True),
            )
            .all()
        ]
        if not meeting_ids:
            return 0

        records = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.scheduled_meeting_id.in_(meeting_ids),
            AttendanceRecord.student_id == student_id,
        ).all()
        attended = sum(1 for record in records if record.status in {AttendanceStatus.present, AttendanceStatus.late})
        return round(attended / len(meeting_ids) * 100)
