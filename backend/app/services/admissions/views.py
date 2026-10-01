from __future__ import annotations

from app.models.admissions import AdmissionApplication
from app.schemas.academic_groups import PersonSummary
from app.schemas.admissions import ApplicationDocumentOut, ApplicationOut


def application_out(application: AdmissionApplication) -> ApplicationOut:
    return ApplicationOut(
        id=application.id, call_id=application.call_id, call_title=application.call.title,
        applicant=PersonSummary.model_validate(application.applicant), protocol=application.protocol,
        birth_date=application.birth_date, schooling=application.schooling, family_income_cents=application.family_income_cents,
        household_size=application.household_size, city=application.city, claims_reserved=application.claims_reserved,
        reserved_verified=application.reserved_verified, review_score=application.review_score, status=application.status,
        ineligibility_reasons=list(application.ineligibility_reasons or []), rank=application.rank, seat_kind=application.seat_kind,
        confirm_until=application.confirm_until, confirmed_at=application.confirmed_at, created_at=application.created_at,
        documents=[ApplicationDocumentOut.model_validate(document) for document in application.documents],
    )
