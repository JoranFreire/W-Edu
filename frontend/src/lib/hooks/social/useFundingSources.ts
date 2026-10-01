'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { FundingSource, FundingSourceInput } from '@/types/socialPrograms';

/** Financiadores da instituicao. */
export function useFundingSources() {
  const request = useCallback(() => api.get<FundingSource[]>(endpoints.social.fundingSources).then((response) => response.data), []);
  const { data = [], error, reload } = useApiQuery(request);
  const create = async (input: FundingSourceInput) => {
    await api.post(endpoints.social.fundingSources, input);
    reload();
  };
  return { fundingSources: data, error, create };
}
