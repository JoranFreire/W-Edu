"""Acesso a dados do almoxarifado."""

from app.repositories.warehouse.items import WarehouseEntryRepository, WarehouseItemRepository
from app.repositories.warehouse.requests import MaterialRequestRepository

__all__ = ["MaterialRequestRepository", "WarehouseEntryRepository", "WarehouseItemRepository"]
