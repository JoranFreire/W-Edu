from app.models.academic import AcademicUnit, Program
from app.repositories.academic._base import Repository


class AcademicUnitRepository(Repository[AcademicUnit]):
    model = AcademicUnit

    def list_all(self) -> list[AcademicUnit]:
        return self.db.query(AcademicUnit).order_by(AcademicUnit.name).all()

    def parent_map(self) -> dict[int, int | None]:
        return dict(self.db.query(AcademicUnit.id, AcademicUnit.parent_id).all())

    def has_children(self, unit_id: int) -> bool:
        return self.db.query(AcademicUnit.id).filter(AcademicUnit.parent_id == unit_id).first() is not None

    def has_programs(self, unit_id: int) -> bool:
        return self.db.query(Program.id).filter(Program.unit_id == unit_id).first() is not None
