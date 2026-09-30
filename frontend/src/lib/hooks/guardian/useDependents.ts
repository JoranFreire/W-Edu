'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Dependent } from '@/types/guardians';

/** Alunos vinculados ao responsavel autenticado. */
export function useDependents() {
  const request = useCallback(() => api.get<Dependent[]>(endpoints.guardians.dependents).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { dependents: data, loading, error };
}
