'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { TeachingOffering } from '@/types/assessment';

/** Turmas que o docente ministra (coordenacao ve todas). */
export function useTeachingOfferings() {
  const request = useCallback(
    () => api.get<TeachingOffering[]>(endpoints.assessment.teachingOfferings).then((response) => response.data),
    [],
  );
  const { data = [], loading, error } = useApiQuery(request);
  return { offerings: data, loading, error };
}
