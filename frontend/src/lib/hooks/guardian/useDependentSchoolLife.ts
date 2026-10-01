'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AgendaItem, Occurrence } from '@/types/schoolLife';

interface DependentSchoolLife {
  occurrences: Occurrence[];
  agenda: AgendaItem[];
}

/** Ocorrencias (com ciencia do responsavel) e agenda da turma de um dependente. */
export function useDependentSchoolLife(studentId: string, fromDate: string) {
  const request = useCallback(async (): Promise<DependentSchoolLife> => {
    const [occurrences, agenda] = await Promise.all([
      api.get<Occurrence[]>(endpoints.guardians.occurrences(studentId)),
      api.get<AgendaItem[]>(endpoints.guardians.agenda(studentId), { params: { from_date: fromDate } }),
    ]);
    return { occurrences: occurrences.data, agenda: agenda.data };
  }, [studentId, fromDate]);
  const { data, error, reload } = useApiQuery(request);

  const acknowledge = async (occurrenceId: string) => {
    await api.post(endpoints.guardians.acknowledge(studentId, occurrenceId));
    reload();
  };

  return { schoolLife: data, error, acknowledge };
}
