from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin, get_current_admin_or_coordinator, get_current_student
from app.models.student import Student
from app.schemas.academic_groups import (
    ClassGroupCreate,
    ClassGroupMemberCreate,
    ClassGroupMemberOut,
    ClassGroupOut,
    ClassGroupUpdate,
)
from app.services.academic import ClassGroupMemberService, ClassGroupService

router = APIRouter(prefix="/class-groups")


@router.get("", response_model=list[ClassGroupOut])
def list_class_groups(
    term_id: int | None = None,
    program_id: int | None = None,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_student),
):
    return ClassGroupService(db).list(term_id=term_id, program_id=program_id)


@router.post("", response_model=ClassGroupOut, status_code=201)
def create_class_group(data: ClassGroupCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return ClassGroupService(db).create(data)


@router.get("/{group_id}", response_model=ClassGroupOut)
def get_class_group(group_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_student)):
    return ClassGroupService(db).detail(group_id)


@router.patch("/{group_id}", response_model=ClassGroupOut)
def update_class_group(
    group_id: int,
    data: ClassGroupUpdate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return ClassGroupService(db).update(group_id, data)


@router.delete("/{group_id}", status_code=204)
def delete_class_group(group_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin)):
    ClassGroupService(db).delete(group_id)


@router.get("/{group_id}/members", response_model=list[ClassGroupMemberOut])
def list_class_group_members(group_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return ClassGroupMemberService(db).list(group_id)


@router.post("/{group_id}/members", response_model=ClassGroupMemberOut, status_code=201)
def add_class_group_member(
    group_id: int,
    data: ClassGroupMemberCreate,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return ClassGroupMemberService(db).add(group_id, data.program_enrollment_id)


@router.delete("/{group_id}/members/{enrollment_id}", status_code=204)
def remove_class_group_member(
    group_id: int,
    enrollment_id: int,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    ClassGroupMemberService(db).remove(group_id, enrollment_id)
