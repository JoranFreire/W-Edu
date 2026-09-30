'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Program } from '@/types/academic';

export function useProgram(programId: number) {
  const request = useCallback(
    () => api.get<Program>(endpoints.academic.program(programId)).then((response) => response.data),
    [programId],
  );
  const { data, loading, error } = useApiQuery(request);
  return { program: data, loading, error };
}
