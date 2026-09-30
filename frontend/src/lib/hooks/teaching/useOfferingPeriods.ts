'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GradingPeriod } from '@/types/academicCalendar';

/** Etapas do periodo letivo da turma (vazio quando a turma nao tem periodo). */
export function useOfferingPeriods(termId: number | null | undefined) {
  const request = useCallback(async () => {
    if (!termId) return [];
    const { data } = await api.get<GradingPeriod[]>(endpoints.academic.gradingPeriods(termId));
    return data;
  }, [termId]);
  const { data = [] } = useApiQuery(request);
  return { periods: data };
}
