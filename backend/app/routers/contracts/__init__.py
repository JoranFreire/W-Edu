"""Rotas dos contratos (/contracts): modelos e emissao (secretaria), partes do contrato e validacao publica."""

from fastapi import APIRouter

from app.routers.contracts import office, party, public, templates

router = APIRouter()
for area in (templates, office, party, public):
    router.include_router(area.router)
