"""Rotas dos perfis de acesso (/access): catalogo, perfis personalizados, atribuicoes e permissoes do usuario."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_access_manager, get_current_student
from app.models.student import Student
from app.schemas.access import AccessRoleInput, AccessRoleOut, AssignmentInput, BuiltInProfileOut, MemberOut, MyAccessOut, PermissionOut
from app.services.access.directory import AccessDirectory
from app.services.access.roles import AccessRoleService

router = APIRouter()


@router.get("/me", response_model=MyAccessOut)
def my_access(current: Student = Depends(get_current_student)):
    return AccessDirectory.mine(current)


@router.get("/permissions", response_model=list[PermissionOut])
def permission_catalog(_: Student = Depends(get_current_access_manager)):
    return AccessDirectory.catalog()


@router.get("/built-in", response_model=list[BuiltInProfileOut])
def built_in_profiles(_: Student = Depends(get_current_access_manager)):
    return AccessDirectory.built_in()


@router.get("/members", response_model=list[MemberOut])
def eligible_members(db: Session = Depends(get_db), _: Student = Depends(get_current_access_manager)):
    return AccessDirectory(db).members()


@router.get("/roles", response_model=list[AccessRoleOut])
def list_roles(db: Session = Depends(get_db), _: Student = Depends(get_current_access_manager)):
    return AccessRoleService(db).list()


@router.post("/roles", response_model=AccessRoleOut, status_code=201)
def create_role(data: AccessRoleInput, db: Session = Depends(get_db), current: Student = Depends(get_current_access_manager)):
    return AccessRoleService(db).create(data, current)


@router.put("/roles/{role_id}", response_model=AccessRoleOut)
def update_role(role_id: int, data: AccessRoleInput, db: Session = Depends(get_db), current: Student = Depends(get_current_access_manager)):
    return AccessRoleService(db).update(role_id, data, current)


@router.delete("/roles/{role_id}", status_code=204)
def delete_role(role_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_access_manager)):
    AccessRoleService(db).delete(role_id, current)


@router.post("/roles/{role_id}/members", response_model=AccessRoleOut)
def assign_role(role_id: int, data: AssignmentInput, db: Session = Depends(get_db), current: Student = Depends(get_current_access_manager)):
    return AccessRoleService(db).assign(role_id, data.user_id, current)


@router.delete("/roles/{role_id}/members/{user_id}", response_model=AccessRoleOut)
def unassign_role(role_id: int, user_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_access_manager)):
    return AccessRoleService(db).unassign(role_id, user_id, current)
