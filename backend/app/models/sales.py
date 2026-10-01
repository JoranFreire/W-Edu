from datetime import datetime, timezone
import enum
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.ids import new_id
from app.models.institution import InstitutionType


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    proposal = "proposal"
    won = "won"
    lost = "lost"


class SalesLead(Base):
    """Interesse em contratar a plataforma, vindo da pagina de contratacao. Global: nao pertence a uma instituicao."""

    __tablename__ = "sales_leads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    institution_name: Mapped[str] = mapped_column(String(200))
    institution_type: Mapped[InstitutionType] = mapped_column(SAEnum(InstitutionType))
    students_estimate: Mapped[int | None] = mapped_column(Integer)
    plan_id: Mapped[UUID | None] = mapped_column(ForeignKey("saas_plans.id", ondelete="SET NULL"), index=True)
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[LeadStatus] = mapped_column(SAEnum(LeadStatus), default=LeadStatus.new, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    plan: Mapped["SaasPlan | None"] = relationship()  # noqa: F821
