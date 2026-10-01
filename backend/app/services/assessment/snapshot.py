from __future__ import annotations
from uuid import UUID

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.assessment import AssessmentItem
from app.models.schedule import ClassOffering
from app.repositories.assessment import AssessmentItemRepository, GradeEntryRepository
from app.schemas.assessment import GradingSchemeOut
from app.services.assessment.averages import ScoredItem, average
from app.services.assessment.schemes import GradingSchemeService

NO_PERIOD = "none"


def period_key(period_id: UUID | None) -> str:
    return str(period_id) if period_id is not None else NO_PERIOD


class OfferingScores:
    """Notas de uma turma carregadas uma vez: medias por etapa sob o esquema da turma."""

    def __init__(self, db: Session, offering: ClassOffering):
        self.scheme: GradingSchemeOut = GradingSchemeService(db).effective_for(offering)
        self.items: list[AssessmentItem] = AssessmentItemRepository(db).list_by_offering(offering.id)
        self.scores = {(g.assessment_item_id, g.class_enrollment_id): g.score for g in GradeEntryRepository(db).by_offering(offering.id)}
        self.items_by_period: dict[str, list[AssessmentItem]] = defaultdict(list)
        for item in self.items:
            self.items_by_period[period_key(item.grading_period_id)].append(item)

    def score(self, item_id: UUID, enrollment_id: UUID) -> float | None:
        return self.scores.get((item_id, enrollment_id))

    def period_average(self, enrollment_id: UUID, key: str) -> float | None:
        scored = [ScoredItem(self.score(item.id, enrollment_id), item.max_score, item.weight) for item in self.items_by_period.get(key, [])]
        return average(scored, self.scheme.formula, self.scheme.min_value, self.scheme.max_value)
