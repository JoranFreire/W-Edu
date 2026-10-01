'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { MyRegistrationWindow } from '@/types/registration';

/** Janelas de matricula abertas para o aluno autenticado. */
export function useMyRegistrationWindows() {
  const request = useCallback(() => api.get<MyRegistrationWindow[]>(endpoints.registration.myWindows).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { windows: data, loading, error };
}
