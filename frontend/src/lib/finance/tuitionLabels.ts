import type { DiscountKind, TuitionBasis } from '@/types/tuition';

export const tuitionBasisLabels: Record<TuitionBasis, string> = {
  program: 'Por programa',
  class_group: 'Por turma-grupo',
  credit: 'Por crédito',
};

export const discountKindLabels: Record<DiscountKind, string> = {
  scholarship: 'Bolsa',
  sibling: 'Irmãos',
  punctuality: 'Pontualidade',
  agreement: 'Convênio',
  other: 'Outro',
};

/** Reais digitados (ex.: "450,50") em centavos. */
export function reaisToCents(value: string): number {
  return Math.round(Number(value.replace(/\./g, '').replace(',', '.')) * 100);
}
