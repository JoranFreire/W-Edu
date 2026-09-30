"""Rotas de responsaveis (/guardians): vinculos (secretaria), portal e vida escolar do dependente."""

from fastapi import APIRouter

from app.routers.guardians import links, portal, school_life

router = APIRouter()
for area in (links, portal, school_life):
    router.include_router(area.router)
