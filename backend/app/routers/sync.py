from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.schemas.sync import DataVersionsOut
from app.services.sync import DataVersionService

router = APIRouter()


@router.get("/versions", response_model=DataVersionsOut)
def data_versions(db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    # Checagem leve do app: so baixa de novo as telas cuja area mudou desde o cache.
    return DataVersionsOut(versions=DataVersionService(db).current())
