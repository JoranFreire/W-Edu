"""Avaliacao: esquemas de nota, plano de avaliacoes por oferta e notas lancadas."""

from datetime import date, datetime, timezone
import enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum as SAEnum, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GradingScale(str, enum.Enum):
    numeric = "numeric"
    concept = "concept"      # notas numericas exibidas como conceito (A, B, C...)


class AverageFormula(str, enum.Enum):
    arithmetic = "arithmetic"
    weighted = "weighted"


class AssessmentKind(str, enum.Enum):
    test = "test"
    assignment = "assignment"
    quiz = "quiz"
    practical = "practical"
    participation = "participation"


class GradingScheme(TenantMixin, Base):
    __tablename__ = "grading_schemes"
    __table_args__ = (UniqueConstraint("institution_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    scale: Mapped[GradingScale] = mapped_column(SAEnum(GradingScale), default=GradingScale.numeric)
    min_value: Mapped[float] = mapped_column(Float, default=0)
    max_value: Mapped[float] = mapped_column(Float, default=10)
    passing_grade: Mapped[float] = mapped_column(Float, default=6)
    formula: Mapped[AverageFormula] = mapped_column(SAEnum(AverageFormula), default=AverageFormula.weighted)
    recovery_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # Percentual minimo de frequencia (0-100) para aprovacao.
    min_attendance: Mapped[float] = mapped_column(Float, default=75)
    # Faixas de conceito: [{"code": "A", "min_value": 9}, ...], da maior para a menor.
    concepts: Mapped[list] = mapped_column(JSON, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AssessmentItem(TenantMixin, Base):
    __tablename__ = "assessment_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    class_offering_id: Mapped[int] = mapped_column(ForeignKey("class_offerings.id", ondelete="CASCADE"), index=True)
    grading_period_id: Mapped[int | None] = mapped_column(ForeignKey("grading_periods.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    kind: Mapped[AssessmentKind] = mapped_column(SAEnum(AssessmentKind), default=AssessmentKind.test)
    weight: Mapped[float] = mapped_column(Float, default=1)
    max_score: Mapped[float] = mapped_column(Float, default=10)
    # Quiz existente cujas tentativas podem ser importadas como nota.
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id"), index=True)
    due_on: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    grading_period: Mapped["GradingPeriod | None"] = relationship()
    grades: Mapped[list["GradeEntry"]] = relationship(back_populates="item", cascade="all, delete-orphan")


class GradeEntry(TenantMixin, Base):
    __tablename__ = "grade_entries"
    __table_args__ = (UniqueConstraint("assessment_item_id", "class_enrollment_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_item_id: Mapped[int] = mapped_column(ForeignKey("assessment_items.id", ondelete="CASCADE"), index=True)
    class_enrollment_id: Mapped[int] = mapped_column(ForeignKey("class_enrollments.id"), index=True)
    score: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    graded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    item: Mapped["AssessmentItem"] = relationship(back_populates="grades")
