"""Rotas da vida escolar (/school): ocorrencias e agenda da turma."""

from fastapi import APIRouter

from app.routers.school_life import agenda, occurrences

router = APIRouter()
for area in (occurrences, agenda):
    router.include_router(area.router)
