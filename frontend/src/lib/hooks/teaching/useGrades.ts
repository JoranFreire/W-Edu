'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GradeRow } from '@/types/assessment';

export interface GradeInput {
  class_enrollment_id: string;
  score: number | null;
  notes: string | null;
}

/** Notas de uma avaliacao para os alunos da turma. */
export function useGrades(itemId: string) {
  const request = useCallback(
    () => api.get<GradeRow[]>(endpoints.assessment.grades(itemId)).then((response) => response.data),
    [itemId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const save = async (grades: GradeInput[]) => {
    await api.put(endpoints.assessment.grades(itemId), grades);
    reload();
  };
  const importQuiz = async () => {
    const { data: result } = await api.post<{ imported: number; without_attempt: number }>(endpoints.assessment.importQuiz(itemId));
    reload();
    return result;
  };

  return { rows: data, loading, error, save, importQuiz };
}
