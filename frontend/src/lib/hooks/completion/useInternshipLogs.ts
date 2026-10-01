'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InternshipLog, InternshipLogInput } from '@/types/completion';

/** Diario de horas de um estagio: o aluno lanca e remove; o orientador valida. `onChange` avisa quem mostra os totais. */
export function useInternshipLogs(internshipId: string, onChange?: () => void) {
  const request = useCallback(
    () => api.get<InternshipLog[]>(endpoints.completion.internshipLogs(internshipId)).then((response) => response.data),
    [internshipId],
  );
  const { data = [], error, reload } = useApiQuery(request);
  const refresh = () => {
    reload();
    onChange?.();
  };

  const add = async (input: InternshipLogInput) => {
    await api.post(endpoints.completion.addInternshipLog(internshipId), input);
    refresh();
  };
  const remove = async (logId: string) => {
    await api.delete(endpoints.completion.myInternshipLog(logId));
    refresh();
  };
  const review = async (logId: string, approved: boolean) => {
    await api.post(endpoints.completion.reviewLog(logId), { approved });
    refresh();
  };

  return { logs: data, error, add, remove, review };
}
