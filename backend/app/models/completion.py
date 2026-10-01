"""Requisitos de conclusao alem das disciplinas: atividades complementares, estagio e TCC."""

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


class ActivityCategory(str, enum.Enum):
    teaching = "teaching"          # ensino (monitoria, cursos)
    research = "research"          # pesquisa (iniciacao cientifica)
    extension = "extension"        # extensao
    cultural = "cultural"          # eventos culturais e esportivos
    professional = "professional"  # experiencia profissional
    other = "other"


class ReviewStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class InternshipStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class FinalProjectStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"        # entregue, aguardando defesa
    approved = "approved"
    failed = "failed"


class ComplementaryActivity(TenantMixin, Base):
    """Atividade complementar declarada pelo aluno; a secretaria aprova as horas que valem."""

    __tablename__ = "complementary_activities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    program_enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    category: Mapped[ActivityCategory] = mapped_column(SAEnum(ActivityCategory), default=ActivityCategory.other)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    occurred_on: Mapped[date] = mapped_column(Date)
    hours_requested: Mapped[int] = mapped_column(Integer)
    hours_approved: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[ReviewStatus] = mapped_column(SAEnum(ReviewStatus), default=ReviewStatus.submitted)
    decision_note: Mapped[str | None] = mapped_column(Text)
    decided_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program_enrollment: Mapped["ProgramEnrollment"] = relationship()


class Internship(TenantMixin, Base):
    """Estagio do aluno: concedente, orientador da instituicao e horas registradas no diario de estagio."""

    __tablename__ = "internships"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    program_enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    company_name: Mapped[str] = mapped_column(String(200))
    supervisor_name: Mapped[str | None] = mapped_column(String(200))   # supervisor na concedente
    advisor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)  # orientador
    # Obrigatorio conta para a carga de estagio do programa; nao obrigatorio e so registro.
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    agreement_number: Mapped[str | None] = mapped_column(String(80))   # termo de compromisso
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    planned_hours: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[InternshipStatus] = mapped_column(SAEnum(InternshipStatus), default=InternshipStatus.in_progress)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program_enrollment: Mapped["ProgramEnrollment"] = relationship()
    advisor: Mapped["Student | None"] = relationship()
    logs: Mapped[list["InternshipLog"]] = relationship(
        back_populates="internship", cascade="all, delete-orphan", order_by="InternshipLog.worked_on"
    )


class InternshipLog(TenantMixin, Base):
    """Registro de horas do estagio (supervisionado): o aluno lanca, o orientador ou a coordenacao valida."""

    __tablename__ = "internship_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    internship_id: Mapped[UUID] = mapped_column(ForeignKey("internships.id", ondelete="CASCADE"), index=True)
    worked_on: Mapped[date] = mapped_column(Date)
    hours: Mapped[int] = mapped_column(Integer)
    activities: Mapped[str] = mapped_column(Text)
    status: Mapped[ReviewStatus] = mapped_column(SAEnum(ReviewStatus), default=ReviewStatus.submitted)
    reviewed_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    internship: Mapped["Internship"] = relationship(back_populates="logs")


class FinalProject(TenantMixin, Base):
    """Trabalho de conclusao de curso: um por matricula, com orientador, defesa e resultado."""

    __tablename__ = "final_projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    program_enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("program_enrollments.id"), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(300))
    advisor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    co_advisor_name: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[FinalProjectStatus] = mapped_column(SAEnum(FinalProjectStatus), default=FinalProjectStatus.in_progress)
    defense_on: Mapped[date | None] = mapped_column(Date)
    grade: Mapped[float | None] = mapped_column(Float)
    committee: Mapped[str | None] = mapped_column(Text)   # banca
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program_enrollment: Mapped["ProgramEnrollment"] = relationship()
    advisor: Mapped["Student | None"] = relationship()
