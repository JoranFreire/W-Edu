'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InstitutionPlan, SubscriptionInput } from '@/types/saas';

/** Plano, uso e faturas de uma instituicao (super admin): assinatura, geracao e baixa de faturas. */
export function useInstitutionPlan(institutionId: number) {
  const request = useCallback(
    () => api.get<InstitutionPlan>(endpoints.saas.institution(institutionId)).then((response) => response.data),
    [institutionId],
  );
  const { data, error, reload } = useApiQuery(request);

  const subscribe = async (input: SubscriptionInput) => {
    await api.put(endpoints.saas.subscription(institutionId), input);
    reload();
  };
  const generateInvoice = async (periodStart: string) => {
    await api.post(endpoints.saas.invoices(institutionId), { period_start: periodStart });
    reload();
  };
  const markPaid = async (invoiceId: number) => {
    await api.post(endpoints.saas.invoicePaid(invoiceId));
    reload();
  };

  return { overview: data, error, subscribe, generateInvoice, markPaid };
}
