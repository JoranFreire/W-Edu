from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.student import Student
from app.repositories.course import CourseRepository
from app.repositories.student import StudentRepository


def get_course_or_404(db: Session, course_id: UUID) -> Course:
    course = CourseRepository(db).get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course


def get_student_or_404(db: Session, student_id: UUID) -> Student:
    student = StudentRepository(db).get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return student
