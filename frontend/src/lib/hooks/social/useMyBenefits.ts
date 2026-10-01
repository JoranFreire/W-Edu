'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Delivery } from '@/types/socialPrograms';

/** Beneficios recebidos pelo aluno. */
export function useMyBenefits() {
  const request = useCallback(() => api.get<Delivery[]>(endpoints.social.myBenefits).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { deliveries: data, loading, error };
}
