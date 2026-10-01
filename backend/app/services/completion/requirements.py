"""Requisitos de conclusao do programa frente ao que o aluno ja cumpriu (funcoes puras)."""

from dataclasses import dataclass

from app.schemas.completion import RequirementOut


@dataclass(frozen=True)
class ProgramTargets:
    mandatory_hours: int
    mandatory_credits: int
    total_hours: int | None
    total_credits: int | None
    complementary_hours: int | None
    internship_hours: int | None
    requires_final_project: bool


@dataclass(frozen=True)
class StudentProgress:
    mandatory_hours_done: int
    hours_done: int
    credits_done: int
    complementary_hours_done: int
    internship_hours_done: int
    final_project_approved: bool


def _item(key: str, label: str, done: int, required: int, unit: str) -> RequirementOut:
    return RequirementOut(key=key, label=label, done=done, required=required, unit=unit, met=done >= required)


def build_requirements(targets: ProgramTargets, progress: StudentProgress) -> list[RequirementOut]:
    """Carga obrigatoria sempre; os demais so quando o programa os exige. Creditos: total do programa ou da matriz obrigatoria."""
    items = [_item("mandatory_hours", "Carga horária obrigatória", progress.mandatory_hours_done, targets.mandatory_hours, "h")]
    if targets.total_hours:
        items.append(_item("total_hours", "Carga horária total", progress.hours_done, targets.total_hours, "h"))
    credits_required = targets.total_credits or targets.mandatory_credits
    if credits_required:
        items.append(_item("credits", "Créditos", progress.credits_done, credits_required, "créditos"))
    if targets.complementary_hours:
        items.append(_item("complementary_hours", "Atividades complementares", progress.complementary_hours_done, targets.complementary_hours, "h"))
    if targets.internship_hours:
        items.append(_item("internship_hours", "Estágio obrigatório", progress.internship_hours_done, targets.internship_hours, "h"))
    if targets.requires_final_project:
        items.append(_item("final_project", "Trabalho de conclusão (TCC)", int(progress.final_project_approved), 1, ""))
    return items


def describe_missing(requirement: RequirementOut) -> str:
    if requirement.key == "final_project":
        return "TCC ainda não aprovado"
    unit = "h" if requirement.unit == "h" else f" {requirement.unit}"
    return f"{requirement.label}: {requirement.done}{unit} de {requirement.required}{unit}"
