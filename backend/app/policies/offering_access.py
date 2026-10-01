"""Quem pode lancar notas e diario de uma oferta."""

from fastapi import HTTPException, status

from app.models.schedule import ClassOffering
from app.models.student import ADMIN_ROLES, Student, UserRole
from app.policies.roles import has_any_role, has_role

COORDINATION = ADMIN_ROLES | {UserRole.coordinator}


def can_manage_all_offerings(user: Student) -> bool:
    return has_any_role(user, COORDINATION)


def ensure_can_teach(user: Student, offering: ClassOffering) -> None:
    """Coordenacao opera qualquer oferta; o instrutor so as que ministra."""
    if can_manage_all_offerings(user):
        return
    if has_role(user, UserRole.instructor) and offering.instructor_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não ministra esta turma")
