"""Rotas dos planos SaaS (/saas): catalogo e assinaturas (super admin) e o plano da instituicao ativa."""

from fastapi import APIRouter

from app.routers.saas import current, institutions, plans

router = APIRouter()
for area in (plans, institutions, current):
    router.include_router(area.router)
