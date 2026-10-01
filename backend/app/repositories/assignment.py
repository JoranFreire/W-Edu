from uuid import UUID

from sqlalchemy.orm import Session

from app.models.assignment import AssignmentSubmission


class AssignmentSubmissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, submission_id: UUID) -> AssignmentSubmission | None:
        return self.db.get(AssignmentSubmission, submission_id)

    def get_by_lesson_and_student(self, lesson_id: UUID, student_id: UUID) -> AssignmentSubmission | None:
        return (
            self.db.query(AssignmentSubmission)
            .filter(
                AssignmentSubmission.lesson_id == lesson_id,
                AssignmentSubmission.student_id == student_id,
            )
            .first()
        )

    def list_by_lesson(self, lesson_id: UUID) -> list[AssignmentSubmission]:
        return (
            self.db.query(AssignmentSubmission)
            .filter(AssignmentSubmission.lesson_id == lesson_id)
            .order_by(AssignmentSubmission.submitted_at.desc())
            .all()
        )

    def create(self, submission: AssignmentSubmission) -> AssignmentSubmission:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def update(self, submission: AssignmentSubmission) -> AssignmentSubmission:
        self.db.commit()
        self.db.refresh(submission)
        return submission
