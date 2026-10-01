"""Acesso a dados do almoxarifado."""

from app.repositories.warehouse.items import WarehouseEntryRepository, WarehouseItemRepository
from app.repositories.warehouse.requests import MaterialRequestRepository
from app.repositories.warehouse.returns import MaterialReturnRepository

__all__ = ["MaterialRequestRepository", "MaterialReturnRepository", "WarehouseEntryRepository", "WarehouseItemRepository"]
