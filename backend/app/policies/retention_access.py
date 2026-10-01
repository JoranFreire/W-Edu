"""Quem acompanha a frequencia da turma: secretaria e coordenacao em qualquer turma; o instrutor nas que ministra."""

from fastapi import HTTPException, status

from app.models.schedule import ClassOffering
from app.models.student import ADMIN_ROLES, Student, UserRole

OFFICE = ADMIN_ROLES | {UserRole.coordinator, UserRole.secretary}


def ensure_can_follow(user: Student, offering: ClassOffering) -> None:
    if user.role in OFFICE or (user.role == UserRole.instructor and offering.instructor_id == user.id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não ministra esta turma")
