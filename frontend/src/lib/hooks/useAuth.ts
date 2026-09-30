'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const store = useAuthStore();
  const { student, fetchStudent, fetchInstitution } = store;
  const studentId = student?.id;

  useEffect(() => {
    if (localStorage.getItem('access_token') && !student) {
      fetchStudent();
    }
  }, [student, fetchStudent]);

  // Atualiza instituicao/branding uma vez por usuario carregado.
  useEffect(() => {
    if (localStorage.getItem('access_token') && studentId) {
      fetchInstitution();
    }
  }, [studentId, fetchInstitution]);

  return {
    ...store,
    isLoading: store.isLoading || !store._hasHydrated,
  };
}
