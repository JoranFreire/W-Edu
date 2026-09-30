from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.assessment import AssessmentKind, GradeEntry
from app.models.student import Student
from app.repositories.assessment import GradeEntryRepository
from app.schemas.academic_groups import PersonSummary
from app.schemas.assessment import GradeInput, GradeRow, QuizImportResult
from app.services.assessment.errors import bad_request
from app.services.assessment.items import AssessmentItemService
from app.services.assessment.offerings import TeachingOfferingService


class GradeService:
    """Lancamento de notas de uma avaliacao para os alunos ativos da turma."""

    def __init__(self, db: Session):
        self.repo = GradeEntryRepository(db)
        self.items = AssessmentItemService(db)
        self.offerings = TeachingOfferingService(db)

    def list(self, item_id: int, user: Student) -> list[GradeRow]:
        item = self.items.get_for_teaching(item_id, user)
        entries = self.repo.by_item(item_id)
        return [
            GradeRow(
                class_enrollment_id=enrollment.id,
                student=PersonSummary.model_validate(enrollment.student),
                score=entries[enrollment.id].score if enrollment.id in entries else None,
                notes=entries[enrollment.id].notes if enrollment.id in entries else None,
            )
            for enrollment in self.offerings.roster(item.class_offering_id)
        ]

    def save(self, item_id: int, grades: list[GradeInput], user: Student) -> list[GradeRow]:
        item = self.items.get_editable(item_id, user)
        valid_ids = {enrollment.id for enrollment in self.offerings.roster(item.class_offering_id)}
        for grade in grades:
            if grade.class_enrollment_id not in valid_ids:
                raise bad_request("Aluno não pertence à turma")
            if grade.score is not None and grade.score > item.max_score:
                raise bad_request(f"Nota acima do máximo ({item.max_score:g})")
        self._upsert(item_id, {g.class_enrollment_id: (g.score, g.notes) for g in grades}, user.id)
        return self.list(item_id, user)

    def import_quiz(self, item_id: int, user: Student) -> QuizImportResult:
        """Melhor tentativa de cada aluno no quiz vinculado, convertida para a nota maxima do item."""
        item = self.items.get_editable(item_id, user)
        if item.kind != AssessmentKind.quiz or item.quiz_id is None:
            raise bad_request("Avaliação não está vinculada a um quiz")
        enrollments = self.offerings.roster(item.class_offering_id)
        best = self.repo.best_quiz_scores(item.quiz_id, [e.student_id for e in enrollments])
        existing = self.repo.by_item(item_id)
        scores = {
            e.id: (round(best[e.student_id] / 100 * item.max_score, 2), existing[e.id].notes if e.id in existing else None)
            for e in enrollments
            if e.student_id in best
        }
        self._upsert(item_id, scores, user.id)
        return QuizImportResult(imported=len(scores), without_attempt=len(enrollments) - len(scores))

    def _upsert(self, item_id: int, values: dict[int, tuple[float | None, str | None]], grader_id: int) -> None:
        existing = self.repo.by_item(item_id)
        now = datetime.now(timezone.utc)
        for enrollment_id, (score, notes) in values.items():
            entry = existing.get(enrollment_id) or self.repo.add(
                GradeEntry(assessment_item_id=item_id, class_enrollment_id=enrollment_id)
            )
            entry.score, entry.notes, entry.graded_by_id, entry.graded_at = score, notes, grader_id, now
        self.repo.commit()
