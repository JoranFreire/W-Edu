'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ConclusionCheck } from '@/types/secretariat';

/** Requisitos de conclusao do programa, conclusao e data de colacao. */
export function useConclusion(enrollmentId: number) {
  const request = useCallback(
    () => api.get<ConclusionCheck>(endpoints.secretariat.conclusion(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const conclude = async (concludedOn: string, ceremonyOn: string | null) => {
    await api.post(endpoints.secretariat.conclusion(enrollmentId), { concluded_on: concludedOn, ceremony_on: ceremonyOn });
    reload();
  };
  const setCeremony = async (ceremonyOn: string) => {
    await api.put(endpoints.secretariat.ceremony(enrollmentId), { ceremony_on: ceremonyOn });
    reload();
  };

  return { check: data, loading, error, conclude, setCeremony };
}
