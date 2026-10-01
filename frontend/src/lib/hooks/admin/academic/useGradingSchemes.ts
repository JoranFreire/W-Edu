'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GradingScheme } from '@/types/assessment';

export type GradingSchemeInput = Omit<GradingScheme, 'id'>;

/** Esquemas de avaliacao da instituicao ativa. */
export function useGradingSchemes() {
  const request = useCallback(() => api.get<GradingScheme[]>(endpoints.assessment.schemes).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: string | null, input: GradingSchemeInput) => {
    if (id) await api.patch(endpoints.assessment.scheme(id), input);
    else await api.post(endpoints.assessment.schemes, input);
    reload();
  };
  const remove = async (id: string) => {
    await api.delete(endpoints.assessment.scheme(id));
    reload();
  };

  return { schemes: data, loading, error, save, remove };
}
