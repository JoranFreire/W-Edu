'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { institutionHeaders } from '@/lib/admissions/publicInstitution';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AdmissionCall, AdmissionResult } from '@/types/admissions';

/** Um edital publicado e, depois da selecao, o resultado por protocolo. */
export function usePublicCall(callId: string, institution: string | null) {
  const request = useCallback(async () => {
    const headers = institutionHeaders(institution);
    const call = (await api.get<AdmissionCall>(endpoints.admissions.publicCall(callId), { headers })).data;
    const result = call.status === 'selected'
      ? (await api.get<AdmissionResult>(endpoints.admissions.publicResult(callId), { headers })).data
      : null;
    return { call, result };
  }, [callId, institution]);
  const { data, loading, error } = useApiQuery(request);
  return { call: data?.call, result: data?.result ?? null, loading, error };
}
