from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import ensure_super_admin_boundary, requested_institution_ref, get_current_student
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.services.institution import InstitutionService
from app.services.student import StudentService

router = APIRouter()


@router.post("", response_model=StudentOut, status_code=201)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    institution_ref: str | None = Depends(requested_institution_ref),
):
    # Cadastro publico: sempre aluno, sem empresa, na instituicao do header/subdominio (ou padrao).
    institution = InstitutionService(db).get_public(institution_ref)
    data = data.model_copy(update={"role": UserRole.student, "organization_id": None})
    return StudentService(db).create(data, institution.id)


@router.get("/me", response_model=StudentOut)
def me(current: Student = Depends(get_current_student)):
    return current


@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return StudentService(db).get_or_404(student_id)


@router.patch("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: UUID,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    if current.id != student_id and current.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário fora do seu escopo")
    if current.role not in ADMIN_ROLES:
        data = StudentUpdate(name=data.name, email=data.email)
    ensure_super_admin_boundary(current, data.role, StudentService(db).get_or_404(student_id))
    return StudentService(db).update(student_id, data)


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_student),
):
    if current.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    ensure_super_admin_boundary(current, target=StudentService(db).get_or_404(student_id))
    StudentService(db).delete(student_id)
