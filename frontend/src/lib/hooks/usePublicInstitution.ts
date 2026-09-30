'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InstitutionSummary } from '@/types/institution';

/** Instituicao do subdominio atual (para telas publicas); null no dominio principal. */
export function usePublicInstitution() {
  const request = useCallback(
    () => api.get<InstitutionSummary>(endpoints.institutions.public).then((response) => response.data).catch(() => null),
    [],
  );
  return useApiQuery(request).data ?? null;
}
