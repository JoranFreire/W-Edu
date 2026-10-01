from __future__ import annotations

from app.models.admissions import AdmissionApplication, ApplicationDocument, ApplicationStatus
from app.repositories.academic._base import Repository


class AdmissionApplicationRepository(Repository[AdmissionApplication]):
    model = AdmissionApplication

    def list_by_call(self, call_id: int) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id)
            .order_by(AdmissionApplication.rank.asc().nullslast(), AdmissionApplication.created_at, AdmissionApplication.id)
            .all()
        )

    def list_by_applicant(self, applicant_id: int) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.applicant_id == applicant_id)
            .order_by(AdmissionApplication.created_at.desc())
            .all()
        )

    def get_for(self, call_id: int, applicant_id: int) -> AdmissionApplication | None:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id, AdmissionApplication.applicant_id == applicant_id)
            .first()
        )

    def with_status(self, call_id: int, statuses: tuple[ApplicationStatus, ...]) -> list[AdmissionApplication]:
        return (
            self.db.query(AdmissionApplication)
            .filter(AdmissionApplication.call_id == call_id, AdmissionApplication.status.in_(statuses))
            .order_by(AdmissionApplication.rank.asc().nullslast(), AdmissionApplication.id)
            .all()
        )

    def count_by_call(self, call_ids: list[int]) -> dict[int, int]:
        if not call_ids:
            return {}
        rows = self.db.query(AdmissionApplication.call_id).filter(AdmissionApplication.call_id.in_(call_ids)).all()
        counts: dict[int, int] = {}
        for (call_id,) in rows:
            counts[call_id] = counts.get(call_id, 0) + 1
        return counts


class ApplicationDocumentRepository(Repository[ApplicationDocument]):
    model = ApplicationDocument
