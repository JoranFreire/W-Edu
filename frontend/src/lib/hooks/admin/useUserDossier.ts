'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { UserDossier } from '@/types/userDossier';

/** Dossie consolidado de uma pessoa da instituicao. */
export function useUserDossier(userId: number) {
  const request = useCallback(() => api.get<UserDossier>(`/admin/users/${userId}/dossier`).then((response) => response.data), [userId]);
  const { data, loading, error, reload } = useApiQuery(request);
  return { dossier: data, loading, error, reload };
}
