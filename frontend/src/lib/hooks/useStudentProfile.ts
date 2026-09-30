'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { StudentProfile } from '@/types/auth';

export type StudentProfileInput = Pick<StudentProfile, 'phone' | 'document' | 'position' | 'department' | 'bio'>;

/** Perfil complementar do usuario e sua atualizacao (junto com o nome). */
export function useStudentProfile(userId: number) {
  const request = useCallback(
    () => api.get<StudentProfile>(`/users/${userId}/student-profile`).then((response) => response.data),
    [userId],
  );
  const query = useApiQuery(request);

  const save = async (name: string, profile: StudentProfileInput) => {
    await api.patch(`/users/${userId}`, { name });
    await api.patch(`/users/${userId}/student-profile`, profile);
  };

  return { profile: query.data, loading: query.loading, error: query.error, save };
}
