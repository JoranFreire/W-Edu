from uuid import UUID

from datetime import datetime, timezone
import enum

from sqlalchemy import JSON, Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin
from app.models.student import UserRole


DEFAULT_INSTITUTION_SLUG = "default"


class InstitutionType(str, enum.Enum):
    school = "school"
    university = "university"
    vocational = "vocational"
    corporate = "corporate"
    mixed = "mixed"


class InstitutionStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    archived = "archived"


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    legal_name: Mapped[str | None] = mapped_column(String(200))
    document: Mapped[str | None] = mapped_column(String(50), index=True)
    type: Mapped[InstitutionType] = mapped_column(SAEnum(InstitutionType), default=InstitutionType.mixed)
    status: Mapped[InstitutionStatus] = mapped_column(SAEnum(InstitutionStatus), default=InstitutionStatus.active)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    branding: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    memberships: Mapped[list["InstitutionMembership"]] = relationship(back_populates="institution", cascade="all, delete-orphan")
    campuses: Mapped[list["Campus"]] = relationship(back_populates="institution", cascade="all, delete-orphan")


class InstitutionMembership(Base):
    __tablename__ = "institution_memberships"
    __table_args__ = (UniqueConstraint("institution_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    institution_id: Mapped[UUID] = mapped_column(ForeignKey("institutions.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.student)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    institution: Mapped["Institution"] = relationship(back_populates="memberships")
    user: Mapped["Student"] = relationship()
    # Papeis da pessoa nesta instituicao (aluno e professor ao mesmo tempo, por exemplo); `role` e o principal.
    member_roles: Mapped[list["MemberRole"]] = relationship(back_populates="membership", cascade="all, delete-orphan", lazy="selectin")

    @property
    def roles(self) -> frozenset[UserRole]:
        return frozenset(item.role for item in self.member_roles) | {self.role}


class MemberRole(Base):
    """Um papel da pessoa na instituicao. Sem TenantMixin, como o vinculo: lido antes de escolher a instituicao."""

    __tablename__ = "institution_member_roles"
    __table_args__ = (UniqueConstraint("membership_id", "role"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    membership_id: Mapped[UUID] = mapped_column(ForeignKey("institution_memberships.id", ondelete="CASCADE"), index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))

    membership: Mapped["InstitutionMembership"] = relationship(back_populates="member_roles")


class Campus(TenantMixin, Base):
    __tablename__ = "campuses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    institution: Mapped["Institution"] = relationship(back_populates="campuses")
    locations: Mapped[list["Location"]] = relationship(back_populates="campus")
