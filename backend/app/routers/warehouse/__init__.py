"""Rotas do almoxarifado (/warehouse): materiais, requisicoes, analise, retirada, devolucao e relatorios."""

from fastapi import APIRouter

from app.routers.warehouse import items, office, reports, requests

router = APIRouter()
for area in (items, requests, office, reports):
    router.include_router(area.router)
