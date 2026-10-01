"""Perfis de acesso da instituicao (RBAC) e quem os recebe."""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AccessRole(TenantMixin, Base):
    """Perfil personalizado: um nome e um conjunto de permissoes do catalogo."""

    __tablename__ = "access_roles"
    __table_args__ = (UniqueConstraint("institution_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    assignments: Mapped[list["AccessRoleAssignment"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class AccessRoleAssignment(TenantMixin, Base):
    __tablename__ = "access_role_assignments"
    __table_args__ = (UniqueConstraint("role_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("access_roles.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    role: Mapped["AccessRole"] = relationship(back_populates="assignments")
    user: Mapped["Student"] = relationship()
