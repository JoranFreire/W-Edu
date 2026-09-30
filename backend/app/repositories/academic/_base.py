from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.core.database import Base

T = TypeVar("T", bound=Base)


class Repository(Generic[T]):
    """Operacoes comuns; cada repositorio concreto so acrescenta suas consultas."""

    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entity_id: int) -> T | None:
        return self.db.get(self.model, entity_id)

    def add(self, entity: T) -> T:
        self.db.add(entity)
        return entity

    def save(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()
