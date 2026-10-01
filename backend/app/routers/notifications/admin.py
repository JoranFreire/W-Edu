from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator
from app.models.student import Student
from app.models.notification import NotificationChannel
from app.schemas.notification import (
    NotificationEventCreate,
    NotificationEventOut,
    NotificationTemplateCreate,
    NotificationTemplateOut,
    NotificationTemplateUpdate,
)
from app.services.notifications.delivery import NotificationDeliveryService
from app.services.notifications.events import NotificationEventService
from app.services.notifications.templates import NotificationTemplateService

router = APIRouter()


@router.get("/templates", response_model=list[NotificationTemplateOut])
def list_templates(db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationTemplateService(db).list()


@router.post("/templates", response_model=NotificationTemplateOut, status_code=201)
def create_template(data: NotificationTemplateCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationTemplateService(db).create(data)


@router.patch("/templates/{key}/{channel}", response_model=NotificationTemplateOut)
def update_template(
    key: str,
    channel: NotificationChannel,
    data: NotificationTemplateUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return NotificationTemplateService(db).update(key, channel, data)


@router.get("/events", response_model=list[NotificationEventOut])
def list_events(limit: int = 100, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationEventService(db).list(limit=limit)


@router.post("/events", response_model=NotificationEventOut, status_code=201)
def create_event(data: NotificationEventCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationEventService(db).create(data)


@router.post("/events/{event_id}/retry", response_model=NotificationEventOut)
def retry_event(event_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationEventService(db).retry(event_id)


@router.post("/events/process-due", response_model=list[NotificationEventOut])
def process_due(limit: int = 100, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return NotificationDeliveryService(db).process_due(limit=limit)
