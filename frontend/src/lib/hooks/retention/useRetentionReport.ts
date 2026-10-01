'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { RetentionReport } from '@/types/retention';

/** Frequencia e risco de evasao da turma; readmissao de quem foi desligado (secretaria e coordenacao). */
export function useRetentionReport(offeringId: string) {
  const request = useCallback(
    () => api.get<RetentionReport>(endpoints.retention.offering(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data, error, reload } = useApiQuery(request);
  const readmit = async (enrollmentId: string) => {
    await api.post(endpoints.retention.readmit(enrollmentId));
    reload();
  };
  return { report: data, error, readmit };
}
