from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.institution import Campus
from app.models.schedule import Location
from app.repositories.schedule import LocationRepository
from app.schemas.schedule import LocationCreate, LocationUpdate


class LocationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LocationRepository(db)

    def create(self, data: LocationCreate) -> Location:
        self._ensure_campus(data.campus_id)
        return self.repo.create(Location(**data.model_dump()))

    def _ensure_campus(self, campus_id: int | None) -> None:
        # Campus e filtrado pela instituicao ativa: de outra instituicao resulta em 404.
        if campus_id is not None and not self.db.get(Campus, campus_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campus não encontrado")

    def get_or_404(self, location_id: int) -> Location:
        location = self.repo.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")
        return location

    def list_all(self) -> list[Location]:
        return self.repo.list_all()

    def update(self, location_id: int, data: LocationUpdate) -> Location:
        location = self.get_or_404(location_id)
        self._ensure_campus(data.campus_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(location, field, value)
        return self.repo.update(location)
