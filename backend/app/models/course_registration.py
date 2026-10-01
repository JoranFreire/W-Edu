"""Matricula por disciplina (perfil universidade): janelas de matricula e horario semanal das ofertas."""

from uuid import UUID

from datetime import datetime, time, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RegistrationWindow(TenantMixin, Base):
    """Periodo em que o aluno escolhe as disciplinas do periodo letivo (de um programa ou de todos)."""

    __tablename__ = "registration_windows"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    term_id: Mapped[UUID] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    # Vazio: vale para todos os programas da instituicao.
    program_id: Mapped[UUID | None] = mapped_column(ForeignKey("programs.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Limites de creditos do aluno no periodo; o minimo so e informado, o maximo bloqueia.
    min_credits: Mapped[int | None] = mapped_column(Integer)
    max_credits: Mapped[int | None] = mapped_column(Integer)
    allow_waitlist: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    term: Mapped["AcademicTerm"] = relationship()
    program: Mapped["Program | None"] = relationship()


class OfferingTimeSlot(TenantMixin, Base):
    """Horario semanal da oferta (dia da semana 0 = segunda), base do choque de horario."""

    __tablename__ = "offering_time_slots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    class_offering_id: Mapped[UUID] = mapped_column(ForeignKey("class_offerings.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)
    starts_at: Mapped[time] = mapped_column(Time)
    ends_at: Mapped[time] = mapped_column(Time)
