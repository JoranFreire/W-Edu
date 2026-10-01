from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.admissions import (
    AdmissionCallCreate, AdmissionCallOut, AdmissionCallUpdate, ApplicationOut, ApplicationReview, CallStatusChange,
    DeadlinesOut, DocumentReviewInput, SelectionOut,
)
from app.services.admissions.calls import AdmissionCallService
from app.services.admissions.convocation import ConvocationService
from app.services.admissions.documents import ApplicationDocumentService
from app.services.admissions.review import ApplicationReviewService
from app.services.admissions.selection import SelectionService

router = APIRouter()


@router.get("/calls", response_model=list[AdmissionCallOut])
def list_calls(db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdmissionCallService(db).list()


@router.post("/calls", response_model=AdmissionCallOut, status_code=201)
def create_call(data: AdmissionCallCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdmissionCallService(db).create(data)


@router.get("/calls/{call_id}", response_model=AdmissionCallOut)
def get_call(call_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdmissionCallService(db).detail(call_id)


@router.patch("/calls/{call_id}", response_model=AdmissionCallOut)
def update_call(call_id: UUID, data: AdmissionCallUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdmissionCallService(db).update(call_id, data)


@router.post("/calls/{call_id}/status", response_model=AdmissionCallOut)
def change_call_status(call_id: UUID, data: CallStatusChange, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return AdmissionCallService(db).change_status(call_id, data.status)


@router.get("/calls/{call_id}/applications", response_model=list[ApplicationOut])
def call_applications(call_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ApplicationReviewService(db).list(call_id)


@router.post("/applications/{application_id}/review", response_model=ApplicationOut)
def review_application(application_id: UUID, data: ApplicationReview, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ApplicationReviewService(db).review(application_id, data)


@router.post("/documents/{document_id}/review", response_model=ApplicationOut)
def review_document(document_id: UUID, data: DocumentReviewInput, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return ApplicationDocumentService(db).review(document_id, data, current)


@router.get("/documents/{document_id}/download")
def download_document(document_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ApplicationDocumentService(db).download(document_id)


@router.post("/calls/{call_id}/select", response_model=SelectionOut)
def run_selection(call_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return SelectionService(db).run(call_id)


@router.post("/calls/{call_id}/process-deadlines", response_model=DeadlinesOut)
def process_deadlines(call_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ConvocationService(db).process_deadlines(call_id)
