'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Integralization } from '@/types/completion';

/** Integralizacao de uma matricula (secretaria). */
export function useIntegralization(enrollmentId: number) {
  const request = useCallback(
    () => api.get<Integralization>(endpoints.completion.integralization(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data, error, reload } = useApiQuery(request);
  return { integralization: data, error, reload };
}
