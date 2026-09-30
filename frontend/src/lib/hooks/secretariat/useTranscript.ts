'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Transcript } from '@/types/secretariat';

/** Historico escolar de uma matricula (visao da secretaria). */
export function useTranscript(enrollmentId: number) {
  const request = useCallback(
    () => api.get<Transcript>(endpoints.secretariat.transcript(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data, error, reload } = useApiQuery(request);
  return { transcript: data, error, reload };
}
