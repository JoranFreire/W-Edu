from sqlalchemy.orm import Session

from app.repositories.data_versions import DataVersionRepository
from app.services.sync.areas import AREAS


class DataVersionService:
    """Versao atual de cada area da instituicao; area sem gravacao ainda esta na versao 0."""

    def __init__(self, db: Session):
        self.repo = DataVersionRepository(db)

    def current(self) -> dict[str, int]:
        stored = self.repo.by_area()
        return {area: stored.get(area, 0) for area in AREAS}
