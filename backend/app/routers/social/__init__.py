"""Rotas dos programas sociais (/social): financiadores, beneficios, entregas, QR de retirada e prestacao de contas."""

from fastapi import APIRouter

from app.routers.social import benefits, deliveries, funding, vouchers

router = APIRouter()
for area in (funding, benefits, deliveries, vouchers):
    router.include_router(area.router)
