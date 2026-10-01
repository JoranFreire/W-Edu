from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_warehouse_manager, get_current_warehouse_user
from app.models.student import Student
from app.schemas.warehouse import EntryCreate, EntryOut, ItemCreate, ItemOut, ItemUpdate
from app.services.warehouse.catalog import WarehouseCatalogService

router = APIRouter(prefix="/items")


@router.get("", response_model=list[ItemOut])
def list_items(only_active: bool = False, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_user)):
    return WarehouseCatalogService(db).list(only_active)


@router.post("", response_model=ItemOut, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return WarehouseCatalogService(db).create(data)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, data: ItemUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return WarehouseCatalogService(db).update(item_id, data)


@router.get("/{item_id}/entries", response_model=list[EntryOut])
def item_entries(item_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_warehouse_manager)):
    return WarehouseCatalogService(db).entries_of(item_id)


@router.post("/{item_id}/entries", response_model=ItemOut, status_code=201)
def receive(item_id: int, data: EntryCreate, db: Session = Depends(get_db), current: Student = Depends(get_current_warehouse_manager)):
    return WarehouseCatalogService(db).receive(item_id, data, current)
