"""Rotas dos programas sociais (/social): financiadores, beneficios, entregas e prestacao de contas."""

from fastapi import APIRouter

from app.routers.social import benefits, deliveries, funding

router = APIRouter()
for area in (funding, benefits, deliveries):
    router.include_router(area.router)
