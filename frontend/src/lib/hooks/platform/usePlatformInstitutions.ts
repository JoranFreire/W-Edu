'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Institution, InstitutionStatus, InstitutionType } from '@/types/institution';

export interface NewInstitutionInput {
  slug: string;
  name: string;
  type: InstitutionType;
  admin: { name: string; email: string; password: string } | null;
}

/** Instituicoes da plataforma (super admin): listagem, criacao e status. */
export function usePlatformInstitutions() {
  const request = useCallback(() => api.get<Institution[]>(endpoints.platform.institutions).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: NewInstitutionInput) => {
    await api.post(endpoints.platform.institutions, input);
    reload();
  };
  const setStatus = async (institution: Institution, status: InstitutionStatus) => {
    await api.patch(endpoints.platform.institution(institution.id), { status });
    reload();
  };

  return { institutions: data, loading, error, create, setStatus };
}
