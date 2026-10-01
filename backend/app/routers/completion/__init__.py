"""Rotas dos requisitos de conclusao (/completion): integralizacao, atividades complementares, estagio, TCC e orientacoes."""

from fastapi import APIRouter

from app.routers.completion import activities, advising, final_projects, integralization, internships

router = APIRouter()
for area in (integralization, activities, internships, final_projects, advising):
    router.include_router(area.router)
