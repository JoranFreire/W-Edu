'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { DiaryAttendanceRow } from '@/types/assessment';

export interface DiaryAttendanceInput {
  class_enrollment_id: number;
  absences: number;
  justified: boolean;
  note: string | null;
}

/** Chamada de um registro de aula. */
export function useDiaryAttendance(entryId: number) {
  const request = useCallback(
    () => api.get<DiaryAttendanceRow[]>(endpoints.assessment.diaryAttendance(entryId)).then((response) => response.data),
    [entryId],
  );
  const { data, loading, error } = useApiQuery(request);

  const save = async (rows: DiaryAttendanceInput[]) => {
    await api.put(endpoints.assessment.diaryAttendance(entryId), rows);
  };

  return { rows: data, loading, error, save };
}
