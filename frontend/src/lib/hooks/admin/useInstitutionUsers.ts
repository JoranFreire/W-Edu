'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { User } from '@/types/auth';

/** Usuarios da instituicao ativa (somente leitura), para seletores. */
export function useInstitutionUsers() {
  const request = useCallback(() => api.get<User[]>('/admin/users').then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { users: data, loading, error };
}
