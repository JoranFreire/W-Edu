'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { DiaryEntry } from '@/types/assessment';

export interface DiaryEntryInput {
  date: string;
  lesson_count: number;
  content_taught: string;
}

/** Registros de aula da turma. */
export function useClassDiary(offeringId: number) {
  const request = useCallback(
    () => api.get<DiaryEntry[]>(endpoints.assessment.diary(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: DiaryEntryInput) => {
    await api.post(endpoints.assessment.diary(offeringId), input);
    reload();
  };
  const remove = async (id: number) => {
    await api.delete(endpoints.assessment.diaryEntry(id));
    reload();
  };

  return { entries: data, loading, error, create, remove };
}
