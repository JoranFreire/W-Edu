from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import ensure_super_admin_boundary, get_current_academic_staff, get_current_admin
from app.models.student import Student, UserRole
from app.policies.user_scope import PRIVILEGED_ROLES, ensure_academic_user_scope
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate
from app.services.student import StudentService

router = APIRouter()


@router.get("/students", response_model=list[StudentOut])
@router.get("/users", response_model=list[StudentOut])
def list_all_students(db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    service = StudentService(db)
    if current.role == UserRole.company_manager:
        return service.list_by_organization(current.organization_id)
    return service.list_all()


@router.post("/students", response_model=StudentOut, status_code=201)
@router.post("/users", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    ensure_super_admin_boundary(current, data.role)
    if current.role in {UserRole.company_manager, UserRole.coordinator}:
        if data.role in PRIVILEGED_ROLES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão para criar este papel")
    if current.role == UserRole.company_manager:
        data = data.model_copy(update={"organization_id": current.organization_id})
    return StudentService(db).create(data)


@router.patch("/students/{student_id}", response_model=StudentOut)
@router.patch("/users/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    ensure_super_admin_boundary(current, data.role, StudentService(db).get_or_404(student_id))
    if current.role in {UserRole.company_manager, UserRole.coordinator}:
        target = StudentService(db).get_or_404(student_id)
        ensure_academic_user_scope(current, target)
    if current.role == UserRole.company_manager:
        data = data.model_copy(update={"organization_id": current.organization_id})
    if current.role in {UserRole.company_manager, UserRole.coordinator} and data.role in PRIVILEGED_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão para atribuir este papel")
    return StudentService(db).update(student_id, data)


@router.delete("/students/{student_id}", status_code=204)
@router.delete("/users/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_admin)):
    ensure_super_admin_boundary(current, target=StudentService(db).get_or_404(student_id))
    StudentService(db).delete(student_id)
