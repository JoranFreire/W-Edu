from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.schedule import ClassEnrollment, ClassOffering
from app.models.student import Student
from app.policies.offering_access import can_manage_all_offerings, ensure_can_teach
from app.repositories.academic import ClassGroupMemberRepository
from app.repositories.assessment import TeachingOfferingRepository
from app.schemas.assessment import SyncEnrollmentsResult
from app.services.assessment.errors import bad_request, not_found


class TeachingOfferingService:
    """Ofertas sob responsabilidade do docente e sua lista de alunos."""

    def __init__(self, db: Session):
        self.repo = TeachingOfferingRepository(db)
        self.group_members = ClassGroupMemberRepository(db)

    def list_for(self, user: Student) -> list[ClassOffering]:
        return self.repo.list(instructor_id=None if can_manage_all_offerings(user) else user.id)

    def get_for_teaching(self, offering_id: UUID, user: Student) -> ClassOffering:
        offering = self.repo.get_by_id(offering_id)
        if not offering:
            raise not_found("Turma não encontrada")
        ensure_can_teach(user, offering)
        return offering

    def roster(self, offering_id: UUID) -> list[ClassEnrollment]:
        return self.repo.roster(offering_id)

    def roster_for_teaching(self, offering_id: UUID, user: Student) -> list[Student]:
        """Alunos da turma vistos por quem a ministra (ou pela coordenacao)."""
        self.get_for_teaching(offering_id, user)
        return [enrollment.student for enrollment in self.repo.roster(offering_id)]

    def sync_group_enrollments(self, offering_id: UUID, user: Student) -> SyncEnrollmentsResult:
        """Inscreve na oferta os alunos da turma-grupo vinculada (escola: a turma herda as disciplinas)."""
        offering = self.get_for_teaching(offering_id, user)
        if offering.class_group_id is None:
            raise bad_request("Turma sem turma-grupo vinculada")
        enrolled = self.repo.enrolled_student_ids(offering_id)
        created = 0
        for member in self.group_members.list_by_group(offering.class_group_id):
            student_id = member.program_enrollment.student_id
            if student_id not in enrolled:
                self.repo.db.add(ClassEnrollment(class_offering_id=offering_id, student_id=student_id))
                enrolled.add(student_id)
                created += 1
        self.repo.commit()
        return SyncEnrollmentsResult(created=created)
