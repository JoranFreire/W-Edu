'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Gradebook } from '@/types/assessment';

/** Boletim parcial da turma (medias por etapa, media geral e frequencia). */
export function useGradebook(offeringId: string) {
  const request = useCallback(
    () => api.get<Gradebook>(endpoints.assessment.gradebook(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data, loading, error, reload } = useApiQuery(request);
  return { gradebook: data, loading, error, reload };
}
