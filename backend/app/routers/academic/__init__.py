"""Rotas da estrutura curricular (/academic), uma area por modulo."""

from fastapi import APIRouter

from app.routers.academic import (
    calendar,
    class_groups,
    components,
    curricula,
    grading_periods,
    program_enrollments,
    programs,
    subject_links,
    subjects,
    terms,
    units,
)

router = APIRouter()
for area in (
    units, programs, subjects, subject_links, curricula, components,
    terms, grading_periods, calendar, program_enrollments, class_groups,
):
    router.include_router(area.router)
