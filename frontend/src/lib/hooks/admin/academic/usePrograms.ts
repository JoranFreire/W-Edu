'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Program, ProgramLevel, ProgramStatus } from '@/types/academic';

export interface ProgramInput {
  code: string;
  name: string;
  level: ProgramLevel;
  unit_id: number | null;
  degree: string | null;
  duration_terms: number | null;
  total_hours: number | null;
  total_credits: number | null;
  status: ProgramStatus;
}

/** Programas da instituicao ativa; toda alteracao recarrega a lista. */
export function usePrograms() {
  const request = useCallback(() => api.get<Program[]>(endpoints.academic.programs).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: number | null, input: ProgramInput) => {
    if (id) await api.patch(endpoints.academic.program(id), input);
    else await api.post(endpoints.academic.programs, input);
    reload();
  };
  const remove = async (program: Program) => {
    await api.delete(endpoints.academic.program(program.id));
    reload();
  };

  return { programs: data, loading, error, save, remove };
}
