'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AcademicTerm, TermKind, TermStatus } from '@/types/academicCalendar';

export interface AcademicTermInput {
  name: string;
  kind: TermKind;
  starts_on: string;
  ends_on: string;
}

/** Periodos letivos da instituicao ativa e seu ciclo de vida. */
export function useAcademicTerms() {
  const request = useCallback(() => api.get<AcademicTerm[]>(endpoints.academic.terms).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: number | null, input: AcademicTermInput) => {
    if (id) await api.patch(endpoints.academic.term(id), input);
    else await api.post(endpoints.academic.terms, input);
    reload();
  };
  const changeStatus = async (id: number, status: TermStatus) => {
    await api.post(endpoints.academic.termStatus(id), { status });
    reload();
  };
  const remove = async (id: number) => {
    await api.delete(endpoints.academic.term(id));
    reload();
  };

  return { terms: data, loading, error, reload, save, changeStatus, remove };
}
