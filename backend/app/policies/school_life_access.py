"""Quem publica agenda da turma e quem remove registros da vida escolar."""

from fastapi import HTTPException, status

from app.models.academic_groups import ClassGroup
from app.models.student import ADMIN_ROLES, Student, UserRole

COORDINATION = ADMIN_ROLES | {UserRole.coordinator}
OFFICE = COORDINATION | {UserRole.secretary}


def ensure_can_publish_agenda(user: Student, group: ClassGroup, teaches_group: bool) -> None:
    """Coordenacao e secretaria publicam em qualquer turma; o instrutor so na que rege ou em que leciona."""
    if user.role in OFFICE:
        return
    if user.role == UserRole.instructor and (group.homeroom_teacher_id == user.id or teaches_group):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não leciona nesta turma")


def ensure_can_remove(user: Student, author_id: int | None) -> None:
    """Remove o registro quem o criou ou a coordenacao."""
    if user.role in COORDINATION or (author_id is not None and author_id == user.id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o autor ou a coordenação pode remover")
