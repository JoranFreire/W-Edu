from __future__ import annotations

from sqlalchemy import func

from app.models.academic_groups import ProgramEnrollment
from app.models.completion import Internship, InternshipLog, InternshipStatus, ReviewStatus
from app.repositories.academic._base import Repository


class InternshipRepository(Repository[Internship]):
    model = Internship

    def list_by_enrollment(self, enrollment_id: int) -> list[Internship]:
        return (
            self.db.query(Internship)
            .filter(Internship.program_enrollment_id == enrollment_id)
            .order_by(Internship.starts_on.desc(), Internship.id.desc())
            .all()
        )

    def list_by_student(self, student_id: int) -> list[Internship]:
        return (
            self.db.query(Internship)
            .join(ProgramEnrollment, ProgramEnrollment.id == Internship.program_enrollment_id)
            .filter(ProgramEnrollment.student_id == student_id)
            .order_by(Internship.starts_on.desc(), Internship.id.desc())
            .all()
        )

    def list_supervised(self, advisor_id: int | None) -> list[Internship]:
        """Estagios em andamento do orientador (sem orientador informado: todos, para a coordenacao)."""
        query = self.db.query(Internship).filter(Internship.status == InternshipStatus.in_progress)
        if advisor_id is not None:
            query = query.filter(Internship.advisor_id == advisor_id)
        return query.order_by(Internship.starts_on, Internship.id).all()

    def hours(self, internship_ids: list[int]) -> dict[int, dict[ReviewStatus, int]]:
        """Horas lancadas por estagio e situacao do registro."""
        if not internship_ids:
            return {}
        rows = (
            self.db.query(InternshipLog.internship_id, InternshipLog.status, func.sum(InternshipLog.hours))
            .filter(InternshipLog.internship_id.in_(internship_ids))
            .group_by(InternshipLog.internship_id, InternshipLog.status)
            .all()
        )
        totals: dict[int, dict[ReviewStatus, int]] = {}
        for internship_id, status, hours in rows:
            totals.setdefault(internship_id, {})[status] = int(hours or 0)
        return totals

    def approved_mandatory_hours(self, enrollment_id: int) -> int:
        total = (
            self.db.query(func.sum(InternshipLog.hours))
            .join(Internship, Internship.id == InternshipLog.internship_id)
            .filter(
                Internship.program_enrollment_id == enrollment_id,
                Internship.is_mandatory.is_(True),
                Internship.status != InternshipStatus.cancelled,
                InternshipLog.status == ReviewStatus.approved,
            )
            .scalar()
        )
        return int(total or 0)


class InternshipLogRepository(Repository[InternshipLog]):
    model = InternshipLog

    def list_by_internship(self, internship_id: int) -> list[InternshipLog]:
        return (
            self.db.query(InternshipLog)
            .filter(InternshipLog.internship_id == internship_id)
            .order_by(InternshipLog.worked_on.desc(), InternshipLog.id.desc())
            .all()
        )
