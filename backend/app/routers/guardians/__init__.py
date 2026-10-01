"""Rotas de responsaveis (/guardians): vinculos (secretaria) e portal do responsavel."""

from fastapi import APIRouter

from app.routers.guardians import links, portal

router = APIRouter()
for area in (links, portal):
    router.include_router(area.router)
