from __future__ import annotations
from uuid import UUID

from app.models.admissions import AdmissionApplication, ApplicationDocument, ApplicationStatus
from app.repositories.academic._base import Repository


class AdmissionApplicationRepository(Repository[AdmissionApplication]):
    model = AdmissionApplication

    def list_by_call(self, call_id: UUID) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id)
            .order_by(AdmissionApplication.rank.asc().nullslast(), AdmissionApplication.created_at, AdmissionApplication.id)
            .all()
        )

    def list_by_applicant(self, applicant_id: UUID) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.applicant_id == applicant_id)
            .order_by(AdmissionApplication.created_at.desc())
            .all()
        )

    def get_for(self, call_id: UUID, applicant_id: UUID) -> AdmissionApplication | None:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id, AdmissionApplication.applicant_id == applicant_id)
            .first()
        )

    def with_status(self, call_id: UUID, statuses: tuple[ApplicationStatus, ...]) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id, AdmissionApplication.status.in_(statuses))
            .order_by(AdmissionApplication.rank.asc().nullslast(), AdmissionApplication.id)
            .all()
        )

    def count_by_call(self, call_ids: list[UUID]) -> dict[UUID, int]:
        if not call_ids:
            return {}
        rows = self.db.query(AdmissionApplication.call_id).filter(AdmissionApplication.call_id.in_(call_ids)).all()
        counts: dict[UUID, int] = {}
        for (call_id,) in rows:
            counts[call_id] = counts.get(call_id, 0) + 1
        return counts


class ApplicationDocumentRepository(Repository[ApplicationDocument]):
    model = ApplicationDocument
