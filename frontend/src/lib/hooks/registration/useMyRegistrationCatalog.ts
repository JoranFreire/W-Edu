'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { RegistrationCatalog, RegistrationResult } from '@/types/registration';

/** Catalogo da janela para o aluno, com inscricao e cancelamento. */
export function useMyRegistrationCatalog(windowId: string) {
  const request = useCallback(
    () => api.get<RegistrationCatalog>(endpoints.registration.myCatalog(windowId)).then((response) => response.data),
    [windowId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const register = async (offeringId: string) => {
    const { data: result } = await api.post<RegistrationResult>(endpoints.registration.myOffering(windowId, offeringId));
    reload();
    return result;
  };
  const drop = async (offeringId: string) => {
    await api.delete(endpoints.registration.myOffering(windowId, offeringId));
    reload();
  };

  return { catalog: data, loading, error, register, drop };
}
