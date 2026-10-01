'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { FinalProject, FinalProjectInput } from '@/types/completion';

/** TCC da matricula (secretaria): tema, orientador e nova tentativa. */
export function useEnrollmentFinalProject(enrollmentId: number) {
  const request = useCallback(
    () => api.get<FinalProject | null>(endpoints.completion.finalProject(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const save = async (input: FinalProjectInput) => {
    await api.put(endpoints.completion.finalProject(enrollmentId), input);
    reload();
  };

  return { project: data ?? null, loading, error, save };
}
