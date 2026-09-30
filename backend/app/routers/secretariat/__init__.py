"""Rotas da secretaria academica (/secretariat), uma area por modulo."""

from fastapi import APIRouter

from app.routers.secretariat import credit_transfers, movements, students, transcript

router = APIRouter()
for area in (movements, credit_transfers, transcript, students):
    router.include_router(area.router)
