from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.saas import SaasPlan
from app.models.sales import LeadStatus, SalesLead
from app.repositories.sales import SalesLeadRepository
from app.schemas.public_site import SalesLeadCreate, SalesLeadOut, SalesLeadUpdate


def lead_out(lead: SalesLead) -> SalesLeadOut:
    return SalesLeadOut(
        id=lead.id, name=lead.name, email=lead.email, phone=lead.phone, institution_name=lead.institution_name,
        institution_type=lead.institution_type, students_estimate=lead.students_estimate, plan_id=lead.plan_id,
        plan_name=lead.plan.name if lead.plan else None, message=lead.message, status=lead.status, notes=lead.notes,
        created_at=lead.created_at,
    )


class SalesLeadService:
    """Interessados em contratar a plataforma: registro publico e acompanhamento pela administracao."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = SalesLeadRepository(db)

    def register(self, data: SalesLeadCreate) -> bool:
        """Registra o interesse; envio de robo (campo-armadilha preenchido) e aceito sem gravar."""
        if data.website:
            return False
        plan_id = data.plan_id if data.plan_id and self._active_plan(data.plan_id) else None
        self.repo.add(SalesLead(**data.model_dump(exclude={"website", "plan_id"}), plan_id=plan_id))
        return True

    def list(self, lead_status: LeadStatus | None = None) -> list[SalesLeadOut]:
        return [lead_out(lead) for lead in self.repo.list(lead_status)]

    def update(self, lead_id: UUID, data: SalesLeadUpdate) -> SalesLeadOut:
        lead = self.repo.get(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interessado não encontrado")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        return lead_out(self.repo.save(lead))

    def _active_plan(self, plan_id: UUID) -> bool:
        plan = self.db.get(SaasPlan, plan_id)
        return bool(plan and plan.is_active)
