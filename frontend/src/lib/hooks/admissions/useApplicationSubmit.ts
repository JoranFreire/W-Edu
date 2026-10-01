'use client';

import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { institutionHeaders } from '@/lib/admissions/publicInstitution';
import { useAuthStore } from '@/store/authStore';
import type { ApplicationAnswers } from '@/types/admissions';

export interface NewAccount {
  name: string;
  email: string;
  password: string;
}

/** Inscricao pela pagina publica: cria a conta na instituicao (se preciso), entra e envia o questionario. */
export function useApplicationSubmit(institution: string | null) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const login = useAuthStore((state) => state.login);

  const submit = async (callId: number, answers: ApplicationAnswers, account: NewAccount | null) => {
    if (account) {
      await api.post('/users', account, { headers: institutionHeaders(institution) });
      await login({ email: account.email, password: account.password, ...(institution ? { institution } : {}) });
    }
    await api.post(endpoints.admissions.apply(callId), answers);
  };

  return { isAuthenticated, submit };
}
