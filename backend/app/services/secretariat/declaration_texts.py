"""Texto das declaracoes (funcoes puras): congelado no momento da emissao."""

from dataclasses import dataclass
from datetime import date

from app.models.secretariat import DeclarationKind

TITLES = {
    DeclarationKind.enrollment: "DECLARACAO DE MATRICULA",
    DeclarationKind.attendance: "DECLARACAO DE FREQUENCIA",
    DeclarationKind.completion: "DECLARACAO DE CONCLUSAO",
}


@dataclass(frozen=True)
class DeclarationData:
    institution: str
    student: str
    registration_number: str
    program: str
    issued_on: date
    term: str | None = None
    attendance: tuple[tuple[str, float | None], ...] = ()
    concluded_on: date | None = None
    ceremony_on: date | None = None


def _br(day: date) -> str:
    return day.strftime("%d/%m/%Y")


def _rate(value: float | None) -> str:
    return "sem aulas registradas" if value is None else f"{value:.1f}%".replace(".", ",")


def declaration_lines(kind: DeclarationKind, data: DeclarationData) -> list[str]:
    head = [f"{data.institution} declara que {data.student},", f"matricula {data.registration_number},"]
    if kind == DeclarationKind.enrollment:
        body = (
            [f"esta regularmente matriculado(a) em {data.program}", f"no periodo letivo {data.term}."]
            if data.term
            else [f"esta regularmente matriculado(a) em {data.program}."]
        )
    elif kind == DeclarationKind.attendance:
        body = [f"aluno(a) de {data.program}, teve no periodo letivo {data.term}", "a seguinte frequencia:"]
        body += [f"- {name}: {_rate(rate)}" for name, rate in data.attendance] or ["- nenhuma turma no periodo"]
    else:
        body = [f"concluiu {data.program} em {_br(data.concluded_on)}."]  # type: ignore[arg-type]
        if data.ceremony_on:
            body.append(f"Colacao de grau realizada em {_br(data.ceremony_on)}.")
    return head + body + [f"Emitida em {_br(data.issued_on)}."]
