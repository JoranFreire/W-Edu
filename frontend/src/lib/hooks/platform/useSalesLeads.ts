'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { LeadStatus, SalesLead } from '@/types/publicSite';

/** Interessados vindos da pagina de contratacao (super admin): lista e acompanhamento. */
export function useSalesLeads(status: LeadStatus | '') {
  const request = useCallback(
    () => api.get<SalesLead[]>(endpoints.platform.leads, { params: status ? { status } : {} }).then((response) => response.data),
    [status],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const update = async (lead: SalesLead, patch: { status?: LeadStatus; notes?: string }) => {
    await api.patch(endpoints.platform.lead(lead.id), patch);
    reload();
  };

  return { leads: data, loading, error, update };
}
