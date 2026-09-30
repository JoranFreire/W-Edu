"""Rotas administrativas (/admin), uma area por modulo."""

from fastapi import APIRouter

from app.routers.admin import enrollments, organizations, quizzes, user_profiles, users

router = APIRouter()
for area in (users, user_profiles, organizations, enrollments, quizzes):
    router.include_router(area.router)
