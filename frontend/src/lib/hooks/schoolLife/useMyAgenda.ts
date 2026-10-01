'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AgendaItem } from '@/types/schoolLife';

/** Agenda das turmas do aluno autenticado a partir de `fromDate`. */
export function useMyAgenda(fromDate: string) {
  const request = useCallback(
    () => api.get<AgendaItem[]>(endpoints.school.myAgenda, { params: { from_date: fromDate } }).then((response) => response.data),
    [fromDate],
  );
  const { data = [], loading, error } = useApiQuery(request);
  return { items: data, loading, error };
}
