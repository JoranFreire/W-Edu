from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_guardian
from app.models.student import Student
from app.schemas.assessment import ReportCardEntry
from app.schemas.guardians import DependentChargeOut, DependentNoticeOut, DependentOut
from app.schemas.secretariat import TranscriptOut
from app.services.guardians.portal import GuardianPortalService

router = APIRouter(prefix="/me/dependents")


@router.get("", response_model=list[DependentOut])
def list_dependents(db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianPortalService(db).dependents(current)


@router.get("/{student_id}/report-card", response_model=list[ReportCardEntry])
def dependent_report_card(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianPortalService(db).report_card(current, student_id)


@router.get("/{student_id}/transcripts", response_model=list[TranscriptOut])
def dependent_transcripts(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianPortalService(db).transcripts_of(current, student_id)


@router.get("/{student_id}/notices", response_model=list[DependentNoticeOut])
def dependent_notices(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianPortalService(db).notices(current, student_id)


@router.get("/{student_id}/charges", response_model=list[DependentChargeOut])
def dependent_charges(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_guardian)):
    return GuardianPortalService(db).charges(current, student_id)
