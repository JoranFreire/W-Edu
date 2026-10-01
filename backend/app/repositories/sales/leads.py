from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.sales import LeadStatus, SalesLead


class SalesLeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, lead: SalesLead) -> SalesLead:
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get(self, lead_id: UUID) -> SalesLead | None:
        return self.db.get(SalesLead, lead_id)

    def list(self, status: LeadStatus | None = None) -> list[SalesLead]:
        query = self.db.query(SalesLead).options(selectinload(SalesLead.plan))
        if status is not None:
            query = query.filter(SalesLead.status == status)
        return query.order_by(SalesLead.created_at.desc()).all()

    def save(self, lead: SalesLead) -> SalesLead:
        self.db.commit()
        self.db.refresh(lead)
        return lead
