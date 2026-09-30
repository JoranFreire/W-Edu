"""Rotas da secretaria academica (/secretariat), uma area por modulo."""

from fastapi import APIRouter

from app.routers.secretariat import conclusion, credit_transfers, declarations, movements, students, transcript

router = APIRouter()
for area in (movements, credit_transfers, transcript, students, declarations, conclusion):
    router.include_router(area.router)
