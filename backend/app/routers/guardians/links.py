from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.guardians import GuardianLinkCreate, GuardianLinkOut, GuardianLinkUpdate
from app.services.guardians.links import GuardianLinkService

router = APIRouter()


@router.get("/students/{student_id}/links", response_model=list[GuardianLinkOut])
def list_links(student_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return GuardianLinkService(db).list(student_id)


@router.post("/students/{student_id}/links", response_model=GuardianLinkOut, status_code=201)
def add_link(student_id: int, data: GuardianLinkCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return GuardianLinkService(db).add(student_id, data)


@router.patch("/links/{link_id}", response_model=GuardianLinkOut)
def update_link(link_id: int, data: GuardianLinkUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return GuardianLinkService(db).update(link_id, data)


@router.delete("/links/{link_id}", status_code=204)
def remove_link(link_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    GuardianLinkService(db).remove(link_id)
