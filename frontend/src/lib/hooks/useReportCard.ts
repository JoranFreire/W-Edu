'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ReportCardEntry } from '@/types/assessment';

/** Boletim do aluno autenticado. */
export function useReportCard() {
  const request = useCallback(() => api.get<ReportCardEntry[]>(endpoints.assessment.myReportCard).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { entries: data, loading, error };
}
