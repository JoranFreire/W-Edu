'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ComponentKind, CurriculumDetail } from '@/types/academic';

export interface ComponentInput {
  subject_id: number;
  term_number: number;
  kind: ComponentKind;
  hours: number | null;
  credits: number | null;
}

/** Componentes, totais e pendencias de uma versao da matriz. */
export function useCurriculumDetail(curriculumId: number | null) {
  const request = useCallback(async () => {
    if (!curriculumId) return undefined;
    const { data } = await api.get<CurriculumDetail>(endpoints.academic.curriculum(curriculumId));
    return data;
  }, [curriculumId]);
  const { data, loading, error, reload } = useApiQuery(request);

  const addComponent = async (input: ComponentInput) => {
    if (!curriculumId) return;
    await api.post(endpoints.academic.curriculumComponents(curriculumId), input);
    reload();
  };
  const updateComponent = async (componentId: number, input: Omit<ComponentInput, 'subject_id'>) => {
    await api.patch(endpoints.academic.component(componentId), input);
    reload();
  };
  const removeComponent = async (componentId: number) => {
    await api.delete(endpoints.academic.component(componentId));
    reload();
  };

  return { detail: data, loading, error, reload, addComponent, updateComponent, removeComponent };
}
