"""Visao calculada da matriz: carga efetiva de cada componente e totais."""

from app.models.academic import ComponentKind, Curriculum, CurriculumComponent
from app.schemas.academic import CurriculumComponentOut, CurriculumTotals, SubjectSummary


def effective_hours(component: CurriculumComponent) -> int:
    return component.hours if component.hours is not None else component.subject.hours


def effective_credits(component: CurriculumComponent) -> int | None:
    return component.credits if component.credits is not None else component.subject.credits


def component_rows(curriculum: Curriculum) -> list[CurriculumComponentOut]:
    return [
        CurriculumComponentOut(
            id=component.id,
            subject=SubjectSummary.model_validate(component.subject),
            term_number=component.term_number,
            kind=component.kind,
            hours=effective_hours(component),
            credits=effective_credits(component),
            hours_override=component.hours,
            credits_override=component.credits,
        )
        for component in curriculum.components
    ]


def totals(curriculum: Curriculum) -> CurriculumTotals:
    components = curriculum.components
    return CurriculumTotals(
        hours=sum(effective_hours(c) for c in components),
        credits=sum(effective_credits(c) or 0 for c in components),
        mandatory_hours=sum(effective_hours(c) for c in components if c.kind == ComponentKind.mandatory),
        terms=max((c.term_number for c in components), default=0),
    )
