"""Financeiro educacional: planos de mensalidade e descontos/bolsas do aluno."""

from uuid import UUID

from datetime import date, datetime, timezone
import enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TuitionBasis(str, enum.Enum):
    program = "program"          # mensalidade fixa de quem esta matriculado no programa
    class_group = "class_group"  # mensalidade fixa dos alunos da turma-grupo
    credit = "credit"            # valor por credito inscrito no periodo, dividido nas parcelas


class DiscountKind(str, enum.Enum):
    scholarship = "scholarship"  # bolsa
    sibling = "sibling"          # irmaos
    punctuality = "punctuality"  # pontualidade: so vale pagando ate o vencimento
    agreement = "agreement"      # convenio
    other = "other"


class TuitionPlan(TenantMixin, Base):
    """Plano de mensalidade de um periodo letivo: base, valor e parcelas."""

    __tablename__ = "tuition_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    basis: Mapped[TuitionBasis] = mapped_column(SAEnum(TuitionBasis), default=TuitionBasis.program)
    term_id: Mapped[UUID] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    program_id: Mapped[UUID | None] = mapped_column(ForeignKey("programs.id"), index=True)
    class_group_id: Mapped[UUID | None] = mapped_column(ForeignKey("class_groups.id"), index=True)
    # Por parcela (programa/turma-grupo) ou por credito no periodo (credito).
    amount_cents: Mapped[int] = mapped_column(Integer)
    installments: Mapped[int] = mapped_column(Integer, default=1)
    first_due_on: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    term: Mapped["AcademicTerm"] = relationship()
    program: Mapped["Program | None"] = relationship()
    class_group: Mapped["ClassGroup | None"] = relationship()


class StudentDiscount(TenantMixin, Base):
    """Bolsa ou desconto da matricula: percentual ou valor fixo por parcela, numa vigencia."""

    __tablename__ = "student_discounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    program_enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    kind: Mapped[DiscountKind] = mapped_column(SAEnum(DiscountKind), default=DiscountKind.other)
    percent: Mapped[float | None] = mapped_column(Float)
    amount_cents: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
