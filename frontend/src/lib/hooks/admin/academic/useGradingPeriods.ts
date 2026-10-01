'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GradingPeriod, GradingPeriodStatus } from '@/types/academicCalendar';

export interface GradingPeriodInput {
  name: string;
  starts_on: string;
  ends_on: string;
  weight: number;
}

/** Etapas de avaliacao de um periodo letivo. */
export function useGradingPeriods(termId: string) {
  const request = useCallback(
    () => api.get<GradingPeriod[]>(endpoints.academic.gradingPeriods(termId)).then((response) => response.data),
    [termId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: string | null, input: GradingPeriodInput) => {
    if (id) await api.patch(endpoints.academic.gradingPeriod(id), input);
    else await api.post(endpoints.academic.gradingPeriods(termId), input);
    reload();
  };
  const changeStatus = async (id: string, status: GradingPeriodStatus) => {
    await api.post(endpoints.academic.gradingPeriodStatus(id), { status });
    reload();
  };
  const remove = async (id: string) => {
    await api.delete(endpoints.academic.gradingPeriod(id));
    reload();
  };

  return { periods: data, loading, error, reload, save, changeStatus, remove };
}
