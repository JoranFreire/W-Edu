from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.academic import ProgramLevel, ProgramStatus
from app.models.student import Student
from app.schemas.academic import ProgramCreate, ProgramOut, ProgramUpdate
from app.services.academic import ProgramService

router = APIRouter(prefix="/programs")


@router.get("", response_model=list[ProgramOut])
def list_programs(
    unit_id: UUID | None = None,
    level: ProgramLevel | None = None,
    status: ProgramStatus | None = None,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_student),
):
    return ProgramService(db).list(unit_id=unit_id, level=level, status=status)


@router.post("", response_model=ProgramOut, status_code=201)
def create_program(data: ProgramCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return ProgramService(db).create(data)


@router.get("/{program_id}", response_model=ProgramOut)
def get_program(program_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return ProgramService(db).get_or_404(program_id)


@router.patch("/{program_id}", response_model=ProgramOut)
def update_program(
    program_id: UUID,
    data: ProgramUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return ProgramService(db).update(program_id, data)


@router.delete("/{program_id}", status_code=204)
def delete_program(program_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    ProgramService(db).delete(program_id)
