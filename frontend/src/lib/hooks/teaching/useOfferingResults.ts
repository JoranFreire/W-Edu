'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { OfferingResults } from '@/types/assessment';

export interface RecoveryInput {
  class_enrollment_id: number;
  score: number | null;
}

/** Fechamento de etapas, resultado final, recuperacao e finalizacao da turma. */
export function useOfferingResults(offeringId: number) {
  const request = useCallback(
    () => api.get<OfferingResults>(endpoints.assessment.results(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const run = async (action: () => Promise<unknown>) => {
    await action();
    reload();
  };

  return {
    results: data,
    loading,
    error,
    closePeriod: (periodId: number) => run(() => api.post(endpoints.assessment.closePeriod(offeringId, periodId))),
    reopenPeriod: (periodId: number) => run(() => api.delete(endpoints.assessment.closePeriod(offeringId, periodId))),
    compute: () => run(() => api.post(endpoints.assessment.computeResults(offeringId))),
    saveRecovery: (values: RecoveryInput[]) => run(() => api.put(endpoints.assessment.recovery(offeringId), values)),
    finalize: () => run(() => api.post(endpoints.assessment.finalize(offeringId))),
  };
}
