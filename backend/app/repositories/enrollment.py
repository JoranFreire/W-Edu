from uuid import UUID

from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: UUID) -> Enrollment | None:
        return self.db.get(Enrollment, enrollment_id)

    def get_by_student_and_course(self, student_id: UUID, course_id: UUID) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
            .first()
        )

    def list_by_student(self, student_id: UUID) -> list[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.student_id == student_id).all()

    def list_by_course(self, course_id: UUID) -> list[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    def create(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def delete(self, enrollment: Enrollment) -> None:
        self.db.delete(enrollment)
        self.db.commit()
