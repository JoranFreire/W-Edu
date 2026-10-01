import type { GuardianRelationship } from '@/types/guardians';

export const relationshipLabels: Record<GuardianRelationship, string> = {
  mother: 'Mãe',
  father: 'Pai',
  legal_guardian: 'Responsável legal',
  grandparent: 'Avó/Avô',
  other: 'Outro',
};

export function formatMoney(cents: number, currency = 'BRL'): string {
  return (cents / 100).toLocaleString('pt-BR', { style: 'currency', currency });
}
