'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import { useAuthStore } from '@/store/authStore';
import type { Institution, InstitutionBranding, InstitutionType } from '@/types/institution';

export interface InstitutionInput {
  name: string;
  legal_name: string | null;
  document: string | null;
  type: InstitutionType;
  branding: InstitutionBranding;
}

/** Instituicao ativa e sua atualizacao; ao salvar, atualiza tambem o estado global (branding). */
export function useCurrentInstitution() {
  const fetchInstitution = useAuthStore((state) => state.fetchInstitution);
  const request = useCallback(() => api.get<Institution>(endpoints.institutions.current).then((response) => response.data), []);
  const query = useApiQuery(request);

  const save = async (input: InstitutionInput) => {
    await api.patch<Institution>(endpoints.institutions.current, input);
    query.reload();
    await fetchInstitution();
  };

  return { institution: query.data, loading: query.loading, error: query.error, save };
}
