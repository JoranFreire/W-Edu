from fastapi import HTTPException, status

from app.models.student import ADMIN_ROLES, InstructorAvailability, Student, UserRole
from app.services.student import StudentService

MANAGEABLE_ACADEMIC_ROLES = {UserRole.student, UserRole.instructor}
PRIVILEGED_ROLES = ADMIN_ROLES | {UserRole.coordinator, UserRole.company_manager, UserRole.secretary}


def ensure_academic_user_scope(current: Student, target: Student) -> None:
    """Coordenacao e gestores so gerem alunos/instrutores; gestores, apenas da propria empresa."""
    if current.role in ADMIN_ROLES:
        return
    if current.role == UserRole.company_manager and target.organization_id != current.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário fora da empresa")
    if target.role not in MANAGEABLE_ACADEMIC_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil fora do escopo")


def ensure_availability_scope(current: Student, service: StudentService, availability_id: int) -> InstructorAvailability:
    availability = service.availability_repo.get_by_id(availability_id)
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disponibilidade não encontrada")
    instructor = service.get_or_404(availability.instructor_profile.student_id)
    ensure_academic_user_scope(current, instructor)
    return availability
