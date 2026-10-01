from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QuizQuestionCreate(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct_index: int
    order: int = 0


class QuizQuestionUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    correct_index: Optional[int] = None
    order: Optional[int] = None


class QuizQuestionOut(BaseModel):
    id: UUID
    quiz_id: UUID
    question: str
    options: list[str]
    order: int
    model_config = {"from_attributes": True}


class QuizQuestionWithAnswer(QuizQuestionOut):
    correct_index: int


class QuizCreate(BaseModel):
    lesson_id: UUID
    passing_score: int = Field(default=70, ge=1, le=100)
    max_attempts: int = Field(default=0, ge=0)


class QuizUpdate(BaseModel):
    passing_score: Optional[int] = Field(default=None, ge=1, le=100)
    max_attempts: Optional[int] = Field(default=None, ge=0)


class QuizOut(BaseModel):
    id: UUID
    lesson_id: UUID
    passing_score: int
    max_attempts: int
    created_at: datetime
    model_config = {"from_attributes": True}


class QuizWithQuestions(QuizOut):
    questions: list[QuizQuestionOut]


class QuizWithAnswers(QuizOut):
    questions: list[QuizQuestionWithAnswer]


class QuizAnswerSubmit(BaseModel):
    answers: dict[str, int]  # {str(question_id): selected_index}


class QuizAttemptOut(BaseModel):
    id: UUID
    quiz_id: UUID
    student_id: UUID
    score: int
    passed: bool
    answers: dict
    attempted_at: datetime
    model_config = {"from_attributes": True}
