"""Rotas de notificacao (/notifications): templates e eventos (coordenacao) e caixa de avisos do usuario."""

from fastapi import APIRouter

from app.routers.notifications import admin, inbox

router = APIRouter()
for area in (inbox, admin):
    router.include_router(area.router)
