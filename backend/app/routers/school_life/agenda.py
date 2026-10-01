from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_school_staff, get_current_student
from app.models.student import Student
from app.schemas.school_life import AgendaItemCreate, AgendaItemOut
from app.services.school_life.agenda import AgendaService

router = APIRouter()


@router.get("/class-groups/{group_id}/agenda", response_model=list[AgendaItemOut])
def group_agenda(
    group_id: int, from_date: date | None = None, db: Session = Depends(get_db), _: Student = Depends(get_current_school_staff),
):
    return AgendaService(db).list_for_group(group_id, from_date)


@router.post("/class-groups/{group_id}/agenda", response_model=AgendaItemOut, status_code=201)
def publish_agenda_item(
    group_id: int, data: AgendaItemCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff),
):
    return AgendaService(db).publish(group_id, data, current)


@router.delete("/agenda/{item_id}", status_code=204)
def remove_agenda_item(item_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_school_staff)):
    AgendaService(db).remove(item_id, current)


@router.get("/my/agenda", response_model=list[AgendaItemOut])
def my_agenda(from_date: date | None = None, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return AgendaService(db).for_student(current.id, from_date)
