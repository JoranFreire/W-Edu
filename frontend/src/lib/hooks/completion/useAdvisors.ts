'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { PersonSummary } from '@/types/academicGroups';

/** Docentes e coordenadores que podem orientar estagio e TCC. */
export function useAdvisors() {
  const request = useCallback(() => api.get<PersonSummary[]>(endpoints.completion.advisors).then((response) => response.data), []);
  const { data = [] } = useApiQuery(request);
  return data;
}
