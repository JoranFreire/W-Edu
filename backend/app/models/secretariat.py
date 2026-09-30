"""Secretaria academica: movimentacoes da matricula, rematricula e aproveitamento de estudos."""

from datetime import datetime, timezone
import enum

from sqlalchemy import JSON, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EnrollmentEventKind(str, enum.Enum):
    enrolled = "enrolled"
    reenrolled = "reenrolled"                    # rematricula no periodo
    locked = "locked"                            # trancamento
    reactivated = "reactivated"                  # destrancamento
    cancelled = "cancelled"
    dropped = "dropped"                          # evasao
    transferred_out = "transferred_out"          # transferencia externa
    transferred_internal = "transferred_internal"  # mudanca de programa na instituicao
    curriculum_changed = "curriculum_changed"    # migracao de matriz
    graduated = "graduated"


class CreditTransferOrigin(str, enum.Enum):
    internal = "internal"    # cursada em outro programa da instituicao
    external = "external"    # cursada em outra instituicao


class CreditTransferStatus(str, enum.Enum):
    requested = "requested"
    approved = "approved"
    rejected = "rejected"


class ProgramEnrollmentEvent(TenantMixin, Base):
    """Linha do tempo da matricula (auditoria da secretaria)."""

    __tablename__ = "program_enrollment_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_enrollment_id: Mapped[int] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    kind: Mapped[EnrollmentEventKind] = mapped_column(SAEnum(EnrollmentEventKind))
    term_id: Mapped[int | None] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    reason: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TermRegistration(TenantMixin, Base):
    """Rematricula: confirmacao do vinculo do aluno em um periodo letivo."""

    __tablename__ = "term_registrations"
    __table_args__ = (UniqueConstraint("program_enrollment_id", "term_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_enrollment_id: Mapped[int] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    # Serie/semestre que o aluno cursa no periodo.
    curriculum_term_number: Mapped[int | None] = mapped_column(Integer)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    term: Mapped["AcademicTerm"] = relationship()


class CreditTransfer(TenantMixin, Base):
    """Aproveitamento de estudos: disciplina da matriz dispensada por estudo anterior."""

    __tablename__ = "credit_transfers"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_enrollment_id: Mapped[int] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    origin: Mapped[CreditTransferOrigin] = mapped_column(SAEnum(CreditTransferOrigin), default=CreditTransferOrigin.external)
    source_institution: Mapped[str | None] = mapped_column(String(200))
    source_subject: Mapped[str] = mapped_column(String(200))
    grade: Mapped[float | None] = mapped_column(Float)
    hours: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[CreditTransferStatus] = mapped_column(SAEnum(CreditTransferStatus), default=CreditTransferStatus.requested)
    decision_note: Mapped[str | None] = mapped_column(Text)
    decided_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    subject: Mapped["Subject"] = relationship()
