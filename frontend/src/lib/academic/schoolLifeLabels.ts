import type { AgendaItemKind, OccurrenceKind, OccurrenceSeverity } from '@/types/schoolLife';

export const occurrenceKindLabels: Record<OccurrenceKind, string> = {
  behavior: 'Comportamento',
  lateness: 'Atraso',
  material: 'Material/uniforme',
  health: 'Saúde',
  merit: 'Elogio',
  other: 'Outros',
};

export const occurrenceSeverityLabels: Record<OccurrenceSeverity, string> = {
  low: 'Leve',
  medium: 'Média',
  high: 'Grave',
};

export const agendaKindLabels: Record<AgendaItemKind, string> = {
  homework: 'Tarefa de casa',
  test: 'Prova',
  event: 'Evento',
  notice: 'Aviso',
};
