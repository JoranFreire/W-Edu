import type { PlatformInvoiceStatus, SaasSubscriptionStatus } from '@/types/saas';

export const subscriptionStatusLabels: Record<SaasSubscriptionStatus, string> = {
  trial: 'Em teste',
  active: 'Ativa',
  past_due: 'Em atraso',
  cancelled: 'Cancelada',
};

export const invoiceStatusLabels: Record<PlatformInvoiceStatus, string> = {
  pending: 'Em aberto',
  paid: 'Paga',
  cancelled: 'Cancelada',
};
