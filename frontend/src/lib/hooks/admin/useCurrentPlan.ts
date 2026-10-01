'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InstitutionPlan } from '@/types/saas';

/** Plano contratado pela instituicao ativa, uso de alunos e faturas. */
export function useCurrentPlan() {
  const request = useCallback(() => api.get<InstitutionPlan>(endpoints.saas.current).then((response) => response.data), []);
  const { data, error } = useApiQuery(request);
  return { overview: data, error };
}
