from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.schemas.notification import InboxNoticeOut, InboxSummaryOut
from app.services.notifications.inbox import NotificationInboxService

router = APIRouter(prefix="/me")


@router.get("", response_model=list[InboxNoticeOut])
def my_notices(unread_only: bool = False, limit: int = 50, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return NotificationInboxService(db).list(current, unread_only=unread_only, limit=limit)


@router.get("/summary", response_model=InboxSummaryOut)
def my_inbox_summary(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return NotificationInboxService(db).summary(current)


@router.post("/read-all", response_model=InboxSummaryOut)
def mark_all_read(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return NotificationInboxService(db).mark_all_read(current)


@router.post("/{event_id}/read", response_model=InboxNoticeOut)
def mark_read(event_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return NotificationInboxService(db).mark_read(current, event_id)
