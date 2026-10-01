from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.schemas.contracts import ContractTemplateCreate, ContractTemplateOut, ContractTemplateUpdate
from app.services.contracts.templates import ContractTemplateService

router = APIRouter(prefix="/templates")


@router.get("", response_model=list[ContractTemplateOut])
def list_templates(db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ContractTemplateService(db).list()


@router.post("", response_model=ContractTemplateOut, status_code=201)
def create_template(data: ContractTemplateCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ContractTemplateService(db).create(data)


@router.patch("/{template_id}", response_model=ContractTemplateOut)
def update_template(template_id: UUID, data: ContractTemplateUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ContractTemplateService(db).update(template_id, data)
