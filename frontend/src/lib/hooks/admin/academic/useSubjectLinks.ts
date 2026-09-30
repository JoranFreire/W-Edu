'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { SubjectSummary } from '@/types/academic';

export type SubjectLinkKind = 'prerequisites' | 'equivalences';

const listUrl = (kind: SubjectLinkKind, subjectId: number) =>
  kind === 'prerequisites' ? endpoints.academic.prerequisites(subjectId) : endpoints.academic.equivalences(subjectId);

const itemUrl = (kind: SubjectLinkKind, subjectId: number, otherId: number) =>
  kind === 'prerequisites' ? endpoints.academic.prerequisite(subjectId, otherId) : endpoints.academic.equivalence(subjectId, otherId);

/** Pre-requisitos ou equivalencias de uma disciplina. */
export function useSubjectLinks(kind: SubjectLinkKind, subjectId: number) {
  const request = useCallback(
    () => api.get<SubjectSummary[]>(listUrl(kind, subjectId)).then((response) => response.data),
    [kind, subjectId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const add = async (otherId: number) => {
    await api.post(listUrl(kind, subjectId), { subject_id: otherId });
    reload();
  };
  const remove = async (otherId: number) => {
    await api.delete(itemUrl(kind, subjectId, otherId));
    reload();
  };

  return { links: data, loading, error, add, remove };
}
