"""Quem ve e quem valida os requisitos de conclusao do aluno (atividades, estagio e TCC)."""

from uuid import UUID

from fastapi import HTTPException, status

from app.models.academic_groups import ProgramEnrollment, ProgramEnrollmentStatus
from app.models.student import ADMIN_ROLES, Student, UserRole

COORDINATION = ADMIN_ROLES | {UserRole.coordinator}
OFFICE = COORDINATION | {UserRole.secretary}
ADVISOR_ROLES = {UserRole.instructor, UserRole.coordinator}


def ensure_own(enrollment: ProgramEnrollment | None, user: Student) -> ProgramEnrollment:
    """O aluno so mexe nas proprias matriculas (as de outro aluno respondem 404)."""
    if enrollment is None or enrollment.student_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada")
    return enrollment


def ensure_active(enrollment: ProgramEnrollment) -> None:
    if enrollment.status != ProgramEnrollmentStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A matrícula no programa precisa estar ativa")


def ensure_can_supervise(user: Student, advisor_id: UUID | None) -> None:
    """Coordenacao valida qualquer orientacao; o instrutor, so as que orienta."""
    if user.role in COORDINATION or (user.role == UserRole.instructor and advisor_id == user.id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não orienta este aluno")


def ensure_can_view_internship(user: Student, student_id: UUID, advisor_id: UUID | None) -> None:
    if user.id == student_id or user.role in OFFICE or (user.role == UserRole.instructor and advisor_id == user.id):
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")


def ensure_advisor_role(advisor: Student | None) -> None:
    if advisor is not None and advisor.role not in ADVISOR_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O orientador precisa ser docente ou coordenador")
