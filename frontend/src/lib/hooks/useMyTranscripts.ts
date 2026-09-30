'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Transcript } from '@/types/secretariat';

/** Historico escolar do aluno autenticado (uma entrada por matricula em programa). */
export function useMyTranscripts() {
  const request = useCallback(() => api.get<Transcript[]>(endpoints.secretariat.myTranscripts).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { transcripts: data, loading, error };
}
