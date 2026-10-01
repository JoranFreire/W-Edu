from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.institution import Campus
from app.repositories.institution import CampusRepository
from app.schemas.institution import CampusCreate, CampusUpdate


class CampusService:
    def __init__(self, db: Session):
        self.repo = CampusRepository(db)

    def list(self, institution_id: UUID | None = None) -> list[Campus]:
        """Campi da instituicao ativa ou, para a plataforma, de uma instituicao especifica."""
        if institution_id is not None:
            return self.repo.list_by_institution(institution_id)
        return self.repo.list_all()

    def get_or_404(self, campus_id: UUID) -> Campus:
        campus = self.repo.get_by_id(campus_id)
        if not campus:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campus não encontrado")
        return campus

    def create(self, data: CampusCreate) -> Campus:
        return self.repo.create(Campus(**data.model_dump()))

    def update(self, campus_id: UUID, data: CampusUpdate) -> Campus:
        campus = self.get_or_404(campus_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(campus, field, value)
        return self.repo.update(campus)

    def delete(self, campus_id: UUID) -> None:
        campus = self.get_or_404(campus_id)
        if campus.locations:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Campus possui locais vinculados")
        self.repo.delete(campus)
