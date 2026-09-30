"""Rotas da estrutura curricular (/academic), uma area por modulo."""

from fastapi import APIRouter

from app.routers.academic import components, curricula, programs, subject_links, subjects, units

router = APIRouter()
for area in (units, programs, subjects, subject_links, curricula, components):
    router.include_router(area.router)
