"""Contratos de matricula e rematricula: modelo da instituicao e contrato emitido, guardado no GED e aceito eletronicamente."""

from datetime import datetime, timezone
import enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ContractKind(str, enum.Enum):
    enrollment = "enrollment"      # matricula
    reenrollment = "reenrollment"  # rematricula


class ContractStatus(str, enum.Enum):
    pending = "pending"        # aguardando aceite
    signed = "signed"
    cancelled = "cancelled"


class ContractTemplate(TenantMixin, Base):
    """Texto do contrato com campos como {student_name}, {program_name}, {term_name}, {payer_name}."""

    __tablename__ = "contract_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[ContractKind] = mapped_column(SAEnum(ContractKind), default=ContractKind.enrollment)
    body: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EnrollmentContract(TenantMixin, Base):
    """Contrato emitido para a matricula: texto congelado, documento no GED e aceite assinado."""

    __tablename__ = "enrollment_contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_enrollment_id: Mapped[int] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("contract_templates.id"), index=True)
    term_id: Mapped[int | None] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), index=True)
    kind: Mapped[ContractKind] = mapped_column(SAEnum(ContractKind))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[ContractStatus] = mapped_column(SAEnum(ContractStatus), default=ContractStatus.pending)
    validation_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    signer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signature_hash: Mapped[str | None] = mapped_column(String(128))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program_enrollment: Mapped["ProgramEnrollment"] = relationship()
    signer: Mapped["Student | None"] = relationship(foreign_keys=[signer_id])
