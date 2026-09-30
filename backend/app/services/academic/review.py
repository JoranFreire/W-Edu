"""Pendencias de coerencia da matriz; informativas, nao bloqueiam a ativacao."""

from app.models.academic import Curriculum


def curriculum_issues(curriculum: Curriculum, prerequisite_edges: list[tuple[int, int]]) -> list[str]:
    by_subject = {component.subject_id: component for component in curriculum.components}
    issues: list[str] = []
    duration = curriculum.program.duration_terms
    for component in curriculum.components:
        if duration is not None and component.term_number > duration:
            issues.append(
                f"{component.subject.code} está no período {component.term_number}, "
                f"além da duração do programa ({duration})"
            )
    for subject_id, required_id in prerequisite_edges:
        component = by_subject.get(subject_id)
        if component is None:
            continue
        required = by_subject.get(required_id)
        if required is None:
            issues.append(f"{component.subject.code} exige uma disciplina que não está na matriz")
        elif required.term_number >= component.term_number:
            issues.append(
                f"{component.subject.code} (período {component.term_number}) exige "
                f"{required.subject.code}, prevista para o período {required.term_number}"
            )
    return issues
