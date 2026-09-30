'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Campus } from '@/types/institution';

export interface CampusInput {
  name: string;
  address: string | null;
}

/** Campi da instituicao ativa; toda alteracao recarrega a lista. */
export function useCampuses() {
  const request = useCallback(() => api.get<Campus[]>(endpoints.institutions.campuses).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: CampusInput) => {
    await api.post(endpoints.institutions.campuses, input);
    reload();
  };
  const setActive = async (campus: Campus, isActive: boolean) => {
    await api.patch(endpoints.institutions.campus(campus.id), { is_active: isActive });
    reload();
  };
  const remove = async (campus: Campus) => {
    await api.delete(endpoints.institutions.campus(campus.id));
    reload();
  };

  return { campuses: data, loading, error, create, setActive, remove };
}
