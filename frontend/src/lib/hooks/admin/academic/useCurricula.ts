'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Curriculum } from '@/types/academic';

export interface CurriculumInput {
  version: string;
  valid_from: string | null;
}

/** Versoes da matriz curricular de um programa e seu ciclo de vida. */
export function useCurricula(programId: string) {
  const request = useCallback(
    () => api.get<Curriculum[]>(endpoints.academic.programCurricula(programId)).then((response) => response.data),
    [programId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: CurriculumInput) => {
    const { data: created } = await api.post<Curriculum>(endpoints.academic.programCurricula(programId), input);
    reload();
    return created;
  };
  const newVersion = async (sourceId: string, input: CurriculumInput) => {
    const { data: created } = await api.post<Curriculum>(endpoints.academic.curriculumVersions(sourceId), input);
    reload();
    return created;
  };
  const activate = async (id: string) => {
    await api.post(endpoints.academic.curriculumActivate(id));
    reload();
  };
  const archive = async (id: string) => {
    await api.post(endpoints.academic.curriculumArchive(id));
    reload();
  };
  const remove = async (id: string) => {
    await api.delete(endpoints.academic.curriculum(id));
    reload();
  };

  return { curricula: data, loading, error, create, newVersion, activate, archive, remove };
}
