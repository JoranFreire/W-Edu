"""Rotas da matricula por disciplina (/registration): janelas, horarios, aluno e secretaria."""

from fastapi import APIRouter

from app.routers.registration import office, student, time_slots, windows

router = APIRouter()
for area in (windows, time_slots, student, office):
    router.include_router(area.router)
