from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.finance import Charge
from app.models.notification import NotificationEvent
from app.models.student import Student
from app.policies.guardian_access import ensure_financial, ensure_linked
from app.repositories.guardians import GuardianLinkRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import ReportCardEntry
from app.schemas.benefit_vouchers import VoucherOut
from app.schemas.guardians import DependentOut
from app.schemas.secretariat import TranscriptOut
from app.services.assessment.report_card import ReportCardService
from app.services.secretariat.transcript import TranscriptService
from app.services.social.student_vouchers import StudentVoucherService


class GuardianPortalService:
    """Portal do responsavel: dependentes, boletim, historico, comunicados e cobrancas."""

    def __init__(self, db: Session):
        self.repo = GuardianLinkRepository(db)
        self.report_cards = ReportCardService(db)
        self.transcripts = TranscriptService(db)
        self.vouchers = StudentVoucherService(db)

    def dependents(self, guardian: Student) -> list[DependentOut]:
        return [
            DependentOut(
                link_id=link.id, student=PersonSummary.model_validate(link.student), relationship_kind=link.relationship_kind,
                is_financial=link.is_financial, can_pick_up=link.can_pick_up, student_is_adult=link.student.is_adult,
            )
            for link in self.repo.list_by_guardian(guardian.id)
        ]

    def report_card(self, guardian: Student, student_id: UUID) -> list[ReportCardEntry]:
        return self.report_cards.for_student(self._dependent(guardian, student_id))

    def transcripts_of(self, guardian: Student, student_id: UUID) -> list[TranscriptOut]:
        return self.transcripts.for_student(self._dependent(guardian, student_id))

    def notices(self, guardian: Student, student_id: UUID) -> list[NotificationEvent]:
        return self.repo.notices_for(self._dependent(guardian, student_id).id)

    def vouchers_of(self, guardian: Student, student_id: UUID) -> list[VoucherOut]:
        """Beneficios liberados do dependente: o responsavel mostra o QR (criancas sem celular)."""
        return self.vouchers.for_student(self._dependent(guardian, student_id).id)

    def charges(self, guardian: Student, student_id: UUID) -> list[Charge]:
        link = ensure_linked(self.repo.get(student_id, guardian.id))
        ensure_financial(link)
        return self.repo.charges_for(student_id)

    def _dependent(self, guardian: Student, student_id: UUID) -> Student:
        return ensure_linked(self.repo.get(student_id, guardian.id)).student
