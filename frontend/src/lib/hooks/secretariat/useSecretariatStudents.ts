'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { PersonSummary } from '@/types/academicGroups';

/** Alunos da instituicao, para a secretaria matricular. */
export function useSecretariatStudents() {
  const request = useCallback(() => api.get<PersonSummary[]>(endpoints.secretariat.students).then((response) => response.data), []);
  const { data = [] } = useApiQuery(request);
  return { students: data };
}
