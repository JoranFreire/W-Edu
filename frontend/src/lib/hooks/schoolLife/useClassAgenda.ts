'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AgendaItem, AgendaItemInput } from '@/types/schoolLife';

/** Agenda da turma-grupo a partir de `fromDate` (equipe escolar). */
export function useClassAgenda(groupId: string, fromDate: string) {
  const request = useCallback(
    () => api.get<AgendaItem[]>(endpoints.school.groupAgenda(groupId), { params: { from_date: fromDate } }).then((response) => response.data),
    [groupId, fromDate],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const publish = async (input: AgendaItemInput) => {
    await api.post(endpoints.school.groupAgenda(groupId), input);
    reload();
  };
  const remove = async (itemId: string) => {
    await api.delete(endpoints.school.agendaItem(itemId));
    reload();
  };

  return { items: data, error, publish, remove };
}
