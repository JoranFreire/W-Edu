'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AdmissionCall, AdmissionCallInput } from '@/types/admissions';

/** Editais da instituicao (secretaria). */
export function useAdmissionCalls() {
  const request = useCallback(() => api.get<AdmissionCall[]>(endpoints.admissions.calls).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);
  const create = async (input: AdmissionCallInput) => {
    const { data: created } = await api.post<AdmissionCall>(endpoints.admissions.calls, input);
    reload();
    return created;
  };
  return { calls: data, loading, error, create };
}
