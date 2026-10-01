from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_teaching_staff
from app.models.student import Student
from app.schemas.assessment import DiaryAttendanceInput, DiaryAttendanceRow, DiaryEntryCreate, DiaryEntryOut, DiaryEntryUpdate
from app.services.assessment import ClassDiaryService, DiaryAttendanceService

router = APIRouter()


@router.get("/offerings/{offering_id}/diary", response_model=list[DiaryEntryOut])
def list_diary(offering_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return ClassDiaryService(db).list(offering_id, current)


@router.post("/offerings/{offering_id}/diary", response_model=DiaryEntryOut, status_code=201)
def create_diary_entry(
    offering_id: UUID,
    data: DiaryEntryCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_teaching_staff),
):
    return ClassDiaryService(db).create(offering_id, data, current)


@router.patch("/diary-entries/{entry_id}", response_model=DiaryEntryOut)
def update_diary_entry(entry_id: UUID, data: DiaryEntryUpdate, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return ClassDiaryService(db).update(entry_id, data, current)


@router.delete("/diary-entries/{entry_id}", status_code=204)
def delete_diary_entry(entry_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    ClassDiaryService(db).delete(entry_id, current)


@router.get("/diary-entries/{entry_id}/attendance", response_model=list[DiaryAttendanceRow])
def list_diary_attendance(entry_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_teaching_staff)):
    return DiaryAttendanceService(db).list(entry_id, current)


@router.put("/diary-entries/{entry_id}/attendance", response_model=list[DiaryAttendanceRow])
def save_diary_attendance(
    entry_id: UUID,
    data: list[DiaryAttendanceInput],
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_teaching_staff),
):
    return DiaryAttendanceService(db).save(entry_id, data, current)
