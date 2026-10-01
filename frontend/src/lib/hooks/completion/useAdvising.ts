'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Advising, FinalProjectResultInput } from '@/types/completion';

/** Orientacoes em andamento do docente (ou todas, para a coordenacao) e registro do resultado do TCC. */
export function useAdvising() {
  const request = useCallback(() => api.get<Advising>(endpoints.completion.advising).then((response) => response.data), []);
  const { data, loading, error, reload } = useApiQuery(request);

  const recordResult = async (projectId: number, input: FinalProjectResultInput) => {
    await api.post(endpoints.completion.finalProjectResult(projectId), input);
    reload();
  };

  return { advising: data, loading, error, reload, recordResult };
}
