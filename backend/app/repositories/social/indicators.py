from __future__ import annotations
from uuid import UUID

from sqlalchemy import func

from app.models.admissions import AdmissionApplication, AdmissionCall, ApplicationStatus
from app.models.schedule import ClassEnrollment


class SocialIndicatorRepository:
    """Contagens por turma para a prestacao de contas: inscricoes no edital e situacao das matriculas."""

    def __init__(self, db):
        self.db = db

    def applications(self, offering_ids: list[UUID]) -> dict[UUID, int]:
        if not offering_ids:
            return {}
        rows = (
            self.db.query(AdmissionCall.class_offering_id, func.count(AdmissionApplication.id))
            .join(AdmissionApplication, AdmissionApplication.call_id == AdmissionCall.id)
            .filter(AdmissionCall.class_offering_id.in_(offering_ids))
            .group_by(AdmissionCall.class_offering_id)
            .all()
        )
        return dict(rows)

    def enrollments(self, offering_ids: list[UUID]) -> list[ClassEnrollment]:
        if not offering_ids:
            return []
        return self.db.query(ClassEnrollment).filter(ClassEnrollment.class_offering_id.in_(offering_ids)).all()

    def confirmed_answers(self, offering_ids: list[UUID]) -> list[AdmissionApplication]:
        if not offering_ids:
            return []
        return (
            self.db.query(AdmissionApplication)
            .join(AdmissionCall, AdmissionCall.id == AdmissionApplication.call_id)
            .filter(AdmissionCall.class_offering_id.in_(offering_ids), AdmissionApplication.status == ApplicationStatus.confirmed)
            .all()
        )

