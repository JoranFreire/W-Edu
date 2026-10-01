'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const store = useAuthStore();
  const { student, fetchStudent, fetchInstitution, fetchPermissions } = store;
  const studentId = student?.id;

  useEffect(() => {
    if (localStorage.getItem('access_token') && !student) {
      fetchStudent();
    }
  }, [student, fetchStudent]);

  // Atualiza instituicao/branding e permissoes uma vez por usuario carregado.
  useEffect(() => {
    if (localStorage.getItem('access_token') && studentId) {
      fetchInstitution();
      fetchPermissions();
    }
  }, [studentId, fetchInstitution, fetchPermissions]);

  return {
    ...store,
    isLoading: store.isLoading || !store._hasHydrated,
  };
}
