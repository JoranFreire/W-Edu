'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { RegistrationWindow, RegistrationWindowInput } from '@/types/registration';

/** Periodo e programa ficam fixos depois de criada a janela. */
function editableFields(input: RegistrationWindowInput) {
  const { name, opens_at, closes_at, min_credits, max_credits, allow_waitlist } = input;
  return { name, opens_at, closes_at, min_credits, max_credits, allow_waitlist };
}

/** Janelas de matricula por disciplina (secretaria e coordenacao). */
export function useRegistrationWindows() {
  const request = useCallback(() => api.get<RegistrationWindow[]>(endpoints.registration.windows).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: number | null, input: RegistrationWindowInput) => {
    if (id) await api.patch(endpoints.registration.window(id), editableFields(input));
    else await api.post(endpoints.registration.windows, input);
    reload();
  };
  const remove = async (id: number) => {
    await api.delete(endpoints.registration.window(id));
    reload();
  };

  return { windows: data, loading, error, save, remove };
}
