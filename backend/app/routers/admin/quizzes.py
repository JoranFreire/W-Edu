from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator
from app.models.student import Student
from app.schemas.quiz import QuizCreate, QuizOut, QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionWithAnswer, QuizUpdate, QuizWithAnswers
from app.services.quiz import QuizService

router = APIRouter()


@router.post("/quizzes", response_model=QuizOut, status_code=201)
def create_quiz(data: QuizCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return QuizService(db).create_quiz(data)


@router.get("/quizzes/lesson/{lesson_id}", response_model=QuizWithAnswers)
def get_quiz(lesson_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return QuizService(db).get_quiz_with_answers(lesson_id)


@router.patch("/quizzes/lesson/{lesson_id}", response_model=QuizOut)
def update_quiz(lesson_id: UUID, data: QuizUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return QuizService(db).update_quiz(lesson_id, data)


@router.delete("/quizzes/lesson/{lesson_id}", status_code=204)
def delete_quiz(lesson_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    QuizService(db).delete_quiz(lesson_id)


@router.post("/quizzes/lesson/{lesson_id}/questions", response_model=QuizQuestionWithAnswer, status_code=201)
def add_question(lesson_id: UUID, data: QuizQuestionCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return QuizService(db).add_question(lesson_id, data)


@router.patch("/quiz-questions/{question_id}", response_model=QuizQuestionWithAnswer)
def update_question(question_id: UUID, data: QuizQuestionUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return QuizService(db).update_question(question_id, data)


@router.delete("/quiz-questions/{question_id}", status_code=204)
def delete_question(question_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    QuizService(db).delete_question(question_id)
