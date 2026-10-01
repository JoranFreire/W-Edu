"""Quem publica agenda da turma e quem remove registros da vida escolar."""

from uuid import UUID

from fastapi import HTTPException, status

from app.models.academic_groups import ClassGroup
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.policies.roles import has_any_role, has_role

COORDINATION = ADMIN_ROLES | {UserRole.coordinator}
OFFICE = COORDINATION | {UserRole.secretary}


def ensure_can_publish_agenda(user: Student, group: ClassGroup, teaches_group: bool) -> None:
    """Coordenacao e secretaria publicam em qualquer turma; o instrutor so na que rege ou em que leciona."""
    if has_any_role(user, OFFICE):
        return
    if has_role(user, UserRole.instructor) and (group.homeroom_teacher_id == user.id or teaches_group):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não leciona nesta turma")


def ensure_can_view_history(user: Student, teaches_student: bool) -> None:
    """Coordenacao e secretaria veem o historico de qualquer aluno; o instrutor, so de quem ele ensina."""
    if has_any_role(user, OFFICE) or (has_role(user, UserRole.instructor) and teaches_student):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não leciona para este aluno")


def ensure_can_remove(user: Student, author_id: UUID | None) -> None:
    """Remove o registro quem o criou ou a coordenacao."""
    if has_any_role(user, COORDINATION) or (author_id is not None and author_id == user.id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o autor ou a coordenação pode remover")
