"""Rotulos em portugues usados nos comunicados a familia."""

from app.models.school_life import AgendaItemKind, OccurrenceKind

OCCURRENCE_LABELS = {
    OccurrenceKind.behavior: "comportamento",
    OccurrenceKind.lateness: "atraso",
    OccurrenceKind.material: "material/uniforme",
    OccurrenceKind.health: "saúde",
    OccurrenceKind.merit: "elogio",
    OccurrenceKind.other: "outros",
}

AGENDA_LABELS = {
    AgendaItemKind.homework: "Tarefa de casa",
    AgendaItemKind.test: "Prova",
    AgendaItemKind.event: "Evento",
    AgendaItemKind.notice: "Aviso",
}
