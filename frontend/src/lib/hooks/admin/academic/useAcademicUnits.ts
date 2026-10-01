'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AcademicUnit, AcademicUnitKind } from '@/types/academic';

export interface AcademicUnitInput {
  name: string;
  kind: AcademicUnitKind;
  parent_id: string | null;
}

/** Unidades academicas da instituicao ativa; toda alteracao recarrega a lista. */
export function useAcademicUnits() {
  const request = useCallback(() => api.get<AcademicUnit[]>(endpoints.academic.units).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: string | null, input: AcademicUnitInput) => {
    if (id) await api.patch(endpoints.academic.unit(id), input);
    else await api.post(endpoints.academic.units, input);
    reload();
  };
  const remove = async (unit: AcademicUnit) => {
    await api.delete(endpoints.academic.unit(unit.id));
    reload();
  };

  return { units: data, loading, error, save, remove };
}
