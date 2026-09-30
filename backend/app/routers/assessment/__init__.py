"""Rotas de avaliacao e diario (/assessment), uma area por modulo."""

from fastapi import APIRouter

from app.routers.assessment import diary, gradebook, grades, items, results, schemes, teaching

router = APIRouter()
for area in (schemes, teaching, items, grades, gradebook, diary, results):
    router.include_router(area.router)
