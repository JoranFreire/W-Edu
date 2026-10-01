"""Rotas do processo seletivo (/admissions): catalogo publico, candidato e secretaria."""

from fastapi import APIRouter

from app.routers.admissions import applicant, office, public

router = APIRouter()
for area in (public, applicant, office):
    router.include_router(area.router)
