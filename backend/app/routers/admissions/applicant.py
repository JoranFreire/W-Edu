from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.schemas.admissions import ApplicationCreate, ApplicationOut
from app.services.admissions.applications import ApplicationService
from app.services.admissions.convocation import ConvocationService
from app.services.admissions.documents import ApplicationDocumentService

router = APIRouter()


@router.post("/calls/{call_id}/apply", response_model=ApplicationOut, status_code=201)
def apply(call_id: int, data: ApplicationCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ApplicationService(db).apply(current, call_id, data)


@router.get("/my/applications", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ApplicationService(db).list_mine(current)


@router.post("/my/applications/{application_id}/documents", response_model=ApplicationOut, status_code=201)
def upload_document(
    application_id: int, kind: str = Form(...), file: UploadFile = File(...),
    db: Session = Depends(get_db), current: Student = Depends(get_current_student),
):
    return ApplicationDocumentService(db).upload(current, application_id, kind, file)


@router.post("/my/applications/{application_id}/withdraw", response_model=ApplicationOut)
def withdraw(application_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ApplicationService(db).withdraw(current, application_id)


@router.post("/my/applications/{application_id}/confirm", response_model=ApplicationOut)
def confirm(application_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ConvocationService(db).confirm(current, application_id)


@router.post("/my/applications/{application_id}/decline", response_model=ApplicationOut)
def decline(application_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ConvocationService(db).decline(current, application_id)
