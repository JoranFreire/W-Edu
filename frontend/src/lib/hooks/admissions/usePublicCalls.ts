'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { institutionHeaders } from '@/lib/admissions/publicInstitution';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AdmissionCall } from '@/types/admissions';

/** Editais publicados da instituicao (pagina publica de inscricoes). */
export function usePublicCalls(institution: string | null) {
  const request = useCallback(
    () => api.get<AdmissionCall[]>(endpoints.admissions.publicCalls, { headers: institutionHeaders(institution) }).then((response) => response.data),
    [institution],
  );
  const { data = [], loading, error } = useApiQuery(request);
  return { calls: data, loading, error };
}
