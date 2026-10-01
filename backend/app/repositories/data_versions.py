from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_version import DataVersion


class DataVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def by_area(self) -> dict[str, int]:
        """Versoes da instituicao vinculada (filtro de tenant)."""
        return dict(self.db.execute(select(DataVersion.area, DataVersion.version)).all())
