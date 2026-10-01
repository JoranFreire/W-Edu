export const periodLabels: Record<string, string> = { one_time: 'Avulso', monthly: 'Mensal', quarterly: 'Trimestral', yearly: 'Anual' };
export const subscriptionStatusLabels: Record<string, string> = { active: 'Ativa', paused: 'Pausada', cancelled: 'Cancelada', overdue: 'Em atraso', completed: 'Concluída' };
export const chargeStatusLabels: Record<string, string> = { pending: 'Pendente', paid: 'Paga', failed: 'Falhou', cancelled: 'Cancelada', refunded: 'Estornada' };

export const formatCents = (cents: number) => `R$ ${(cents / 100).toFixed(2)}`;

/** Resolve nomes de titulares/planos por id, com fallback "Tipo #id". */
export function makeNameLookup<T extends { id: string; name: string }>(items: T[], fallbackLabel: string) {
  return (id: string | null) => (id ? items.find((item) => item.id === id)?.name ?? `${fallbackLabel} #${id}` : null);
}
