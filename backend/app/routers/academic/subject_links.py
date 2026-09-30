"""Pre-requisitos e equivalencias entre disciplinas."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic import SubjectLinkCreate, SubjectSummary
from app.services.academic import SubjectEquivalenceService, SubjectPrerequisiteService

router = APIRouter(prefix="/subjects/{subject_id}")


@router.get("/prerequisites", response_model=list[SubjectSummary])
def list_prerequisites(subject_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return SubjectPrerequisiteService(db).list(subject_id)


@router.post("/prerequisites", response_model=SubjectSummary, status_code=201)
def add_prerequisite(
    subject_id: int,
    data: SubjectLinkCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return SubjectPrerequisiteService(db).add(subject_id, data.subject_id)


@router.delete("/prerequisites/{required_subject_id}", status_code=204)
def remove_prerequisite(
    subject_id: int,
    required_subject_id: int,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin),
):
    SubjectPrerequisiteService(db).remove(subject_id, required_subject_id)


@router.get("/equivalences", response_model=list[SubjectSummary])
def list_equivalences(subject_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return SubjectEquivalenceService(db).list(subject_id)


@router.post("/equivalences", response_model=SubjectSummary, status_code=201)
def add_equivalence(
    subject_id: int,
    data: SubjectLinkCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return SubjectEquivalenceService(db).add(subject_id, data.subject_id)


@router.delete("/equivalences/{equivalent_subject_id}", status_code=204)
def remove_equivalence(
    subject_id: int,
    equivalent_subject_id: int,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin),
):
    SubjectEquivalenceService(db).remove(subject_id, equivalent_subject_id)
