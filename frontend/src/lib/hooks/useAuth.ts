'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const store = useAuthStore();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('access_token');
    if (token && !store.student) {
      store.fetchStudent();
    }
  }, [store.student]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (localStorage.getItem('access_token') && store.student) {
      store.fetchInstitution();
    }
    // Atualiza instituicao/branding uma vez por carregamento de pagina.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [store.student?.id]);

  return {
    ...store,
    isLoading: store.isLoading || !store._hasHydrated,
  };
}
