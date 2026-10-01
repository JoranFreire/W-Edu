"""Rotas do financeiro educacional (/tuition): planos, geracao, descontos, multa e juros, extratos e baixa."""

from fastapi import APIRouter

from app.routers.tuition import charges, discounts, plans, settings

router = APIRouter()
for area in (plans, settings, discounts, charges):
    router.include_router(area.router)
