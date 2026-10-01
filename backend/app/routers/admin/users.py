from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import ensure_super_admin_boundary, get_current_academic_staff, get_current_admin
from app.models.student import Student, UserRole
from app.policies.roles import has_role, is_admin
from app.policies.user_scope import ensure_academic_user_scope, ensure_can_assign_roles, requested_roles
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate
from app.schemas.user_dossier import UserDossier
from app.services.people.dossier import UserDossierService
from app.services.student import StudentService

router = APIRouter()


@router.get("/students", response_model=list[StudentOut])
@router.get("/users", response_model=list[StudentOut])
def list_all_students(db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    service = StudentService(db)
    if has_role(current, UserRole.company_manager) and not is_admin(current):
        return service.list_by_organization(current.organization_id)
    return service.list_all()


@router.get("/users/{student_id}/dossier", response_model=UserDossier)
def user_dossier(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    return UserDossierService(db).build(current, student_id)


@router.post("/students", response_model=StudentOut, status_code=201)
@router.post("/users", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_academic_staff)):
    ensure_super_admin_boundary(current, data.role, roles=data.roles)
    ensure_can_assign_roles(current, requested_roles(data.role, data.roles))
    if has_role(current, UserRole.company_manager) and not is_admin(current):
        data = data.model_copy(update={"organization_id": current.organization_id})
    return StudentService(db).create(data)


@router.patch("/students/{student_id}", response_model=StudentOut)
@router.patch("/users/{student_id}", response_model=StudentOut)
def update_student(
    student_id: UUID,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_super_admin_boundary(current, data.role, target, roles=data.roles)
    ensure_academic_user_scope(current, target)
    ensure_can_assign_roles(current, requested_roles(data.role, data.roles))
    if has_role(current, UserRole.company_manager) and not is_admin(current):
        data = data.model_copy(update={"organization_id": current.organization_id})
    return StudentService(db).update(student_id, data)


@router.delete("/students/{student_id}", status_code=204)
@router.delete("/users/{student_id}", status_code=204)
def delete_student(student_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_admin)):
    ensure_super_admin_boundary(current, target=StudentService(db).get_or_404(student_id))
    StudentService(db).delete(student_id)
