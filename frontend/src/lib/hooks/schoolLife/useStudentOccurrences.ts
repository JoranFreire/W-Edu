'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Occurrence, OccurrenceInput } from '@/types/schoolLife';

/** Ocorrencias de um aluno (equipe escolar). */
export function useStudentOccurrences(studentId: number) {
  const request = useCallback(
    () => api.get<Occurrence[]>(endpoints.school.studentOccurrences(studentId)).then((response) => response.data),
    [studentId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const register = async (input: OccurrenceInput) => {
    await api.post(endpoints.school.occurrences, input);
    reload();
  };
  const remove = async (occurrenceId: number) => {
    await api.delete(endpoints.school.occurrence(occurrenceId));
    reload();
  };

  return { occurrences: data, error, register, remove };
}
