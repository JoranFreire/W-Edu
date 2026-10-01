import type { LeadStatus } from '@/types/publicSite';

export const leadStatusLabels: Record<LeadStatus, string> = {
  new: 'Novo',
  contacted: 'Em contato',
  proposal: 'Proposta enviada',
  won: 'Fechado',
  lost: 'Perdido',
};
