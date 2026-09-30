"""Responsaveis pelo aluno (escola basica): parentesco, responsavel financeiro e autorizacao de retirada."""

from datetime import datetime, timezone
import enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


class GuardianRelationship(str, enum.Enum):
    mother = "mother"
    father = "father"
    legal_guardian = "legal_guardian"
    grandparent = "grandparent"
    other = "other"


class StudentGuardian(TenantMixin, Base):
    __tablename__ = "student_guardians"
    __table_args__ = (UniqueConstraint("student_id", "guardian_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    guardian_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    relationship_kind: Mapped[GuardianRelationship] = mapped_column(SAEnum(GuardianRelationship), default=GuardianRelationship.other)
    is_financial: Mapped[bool] = mapped_column(Boolean, default=False)
    can_pick_up: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(foreign_keys=[student_id])
    guardian: Mapped["Student"] = relationship(foreign_keys=[guardian_id])
