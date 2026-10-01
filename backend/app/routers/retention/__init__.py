"""Rotas do controle de evasao (/retention): frequencia por aluno, desligamento por faltas e readmissao."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_school_staff, get_current_secretariat
from app.models.student import Student
from app.schemas.retention import EvaluationOut, RetentionReportOut, RetentionRow
from app.services.retention.service import RetentionService

router = APIRouter()


@router.get("/offerings/{offering_id}", response_model=RetentionReportOut)
def retention_report(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    return RetentionService(db).report(offering_id, current)


@router.post("/offerings/{offering_id}/evaluate", response_model=EvaluationOut)
def evaluate_offering(offering_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RetentionService(db).evaluate(offering_id)


@router.post("/enrollments/{enrollment_id}/readmit", response_model=RetentionRow)
def readmit(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return RetentionService(db).readmit(enrollment_id)
