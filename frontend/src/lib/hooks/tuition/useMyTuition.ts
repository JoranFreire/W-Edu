'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { TuitionCharge } from '@/types/tuition';

/** Mensalidades do usuario como aluno ou como responsavel que paga. */
export function useMyTuition() {
  const request = useCallback(() => api.get<TuitionCharge[]>(endpoints.tuition.myCharges).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { charges: data, loading, error };
}
