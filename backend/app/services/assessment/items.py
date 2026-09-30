from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.academic_calendar import GradingPeriod
from app.models.assessment import AssessmentItem
from app.models.schedule import ClassOffering
from app.models.student import Student
from app.policies.assessment_locks import ensure_offering_open, ensure_unlocked, is_period_locked
from app.repositories.academic import GradingPeriodRepository
from app.repositories.assessment import AssessmentItemRepository, PeriodClosureRepository
from app.repositories.quiz import QuizRepository
from app.schemas.assessment import AssessmentItemCreate, AssessmentItemUpdate
from app.services.academic.patch import apply_patch
from app.services.assessment.errors import bad_request, not_found
from app.services.assessment.offerings import TeachingOfferingService


class AssessmentItemService:
    """Plano de avaliacoes da oferta, por etapa."""

    def __init__(self, db: Session):
        self.repo = AssessmentItemRepository(db)
        self.periods = GradingPeriodRepository(db)
        self.quizzes = QuizRepository(db)
        self.closures = PeriodClosureRepository(db)
        self.offerings = TeachingOfferingService(db)

    def list(self, offering_id: int, user: Student) -> list[AssessmentItem]:
        self.offerings.get_for_teaching(offering_id, user)
        return self.repo.list_by_offering(offering_id)

    def create(self, offering_id: int, data: AssessmentItemCreate, user: Student) -> AssessmentItem:
        offering = self.offerings.get_for_teaching(offering_id, user)
        ensure_offering_open(offering)
        period = self._period_for(offering, data.grading_period_id)
        ensure_unlocked(is_period_locked(period, self.closures.closed_period_ids(offering_id)))
        self._validate_quiz(data.quiz_id)
        return self.repo.save(AssessmentItem(class_offering_id=offering_id, **data.model_dump()))

    def get_editable(self, item_id: int, user: Student) -> AssessmentItem:
        item, offering = self._load(item_id, user)
        ensure_offering_open(offering)
        ensure_unlocked(is_period_locked(item.grading_period, self.closures.closed_period_ids(offering.id)))
        return item

    def get_for_teaching(self, item_id: int, user: Student) -> AssessmentItem:
        return self._load(item_id, user)[0]

    def _load(self, item_id: int, user: Student) -> tuple[AssessmentItem, ClassOffering]:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise not_found("Avaliação não encontrada")
        return item, self.offerings.get_for_teaching(item.class_offering_id, user)

    def update(self, item_id: int, data: AssessmentItemUpdate, user: Student) -> AssessmentItem:
        item = self.get_editable(item_id, user)
        if data.quiz_id is not None:
            self._validate_quiz(data.quiz_id)
        if data.max_score is not None and any(g.score is not None and g.score > data.max_score for g in item.grades):
            raise bad_request("Há notas acima da nova nota máxima")
        apply_patch(item, data, clearable=frozenset({"quiz_id", "due_on"}))
        return self.repo.save(item)

    def delete(self, item_id: int, user: Student) -> None:
        self.repo.delete(self.get_editable(item_id, user))

    def _period_for(self, offering: ClassOffering, period_id: int | None) -> GradingPeriod | None:
        if period_id is None:
            return None
        period = self.periods.get_by_id(period_id)
        if not period:
            raise not_found("Etapa de avaliação não encontrada")
        if period.term_id != offering.term_id:
            raise bad_request("A etapa não pertence ao período letivo da turma")
        return period

    def _validate_quiz(self, quiz_id: int | None) -> None:
        if quiz_id is not None and not self.quizzes.get_by_id(quiz_id):
            raise not_found("Quiz não encontrado")
