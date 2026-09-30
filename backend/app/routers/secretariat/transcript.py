from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat, get_current_student
from app.models.student import Student
from app.schemas.secretariat import TranscriptOut
from app.services.secretariat.transcript import TranscriptService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/transcript", response_model=TranscriptOut)
def get_transcript(enrollment_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return TranscriptService(db).for_enrollment(enrollment_id)


@router.get("/my/transcripts", response_model=list[TranscriptOut])
def my_transcripts(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return TranscriptService(db).for_student(current)

