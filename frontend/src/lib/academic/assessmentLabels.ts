import type { AssessmentKind, AverageFormula, GradingScale } from '@/types/assessment';

export const assessmentKindLabels: Record<AssessmentKind, string> = {
  test: 'Prova',
  assignment: 'Trabalho',
  quiz: 'Quiz',
  practical: 'Avaliação prática',
  participation: 'Participação',
};

export const gradingScaleLabels: Record<GradingScale, string> = {
  numeric: 'Numérica',
  concept: 'Conceito',
};

export const averageFormulaLabels: Record<AverageFormula, string> = {
  arithmetic: 'Média aritmética',
  weighted: 'Média ponderada (pesos)',
};

/** Nota formatada no padrao brasileiro (virgula), vazia quando ainda nao lancada. */
export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return value.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
}
