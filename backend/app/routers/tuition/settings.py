from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_finance_staff
from app.models.student import Student
from app.schemas.tuition import LateFeeSettings
from app.services.tuition.late_fees import LateFeeSettingsService

router = APIRouter(prefix="/settings")


@router.get("", response_model=LateFeeSettings)
def get_settings(db: Session = Depends(get_db), _: Student = Depends(get_current_finance_staff)):
    return LateFeeSettingsService(db).get()


@router.put("", response_model=LateFeeSettings)
def update_settings(data: LateFeeSettings, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    return LateFeeSettingsService(db).update(data)
