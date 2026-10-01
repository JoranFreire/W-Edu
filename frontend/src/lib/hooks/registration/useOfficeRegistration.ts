'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { RegistrationCatalog, RegistrationResult } from '@/types/registration';

/** Disciplinas do aluno no periodo pela secretaria (sem janela; `override` dispensa as regras). */
export function useOfficeRegistration(enrollmentId: number, termId: number) {
  const request = useCallback(
    () => api.get<RegistrationCatalog>(endpoints.registration.officeCatalog(enrollmentId, termId)).then((response) => response.data),
    [enrollmentId, termId],
  );
  const { data, loading, error, reload } = useApiQuery(request);

  const register = async (offeringId: number, override: boolean) => {
    const { data: result } = await api.post<RegistrationResult>(endpoints.registration.officeOffering(enrollmentId, offeringId), { override });
    reload();
    return result;
  };
  const drop = async (offeringId: number) => {
    await api.delete(endpoints.registration.officeOffering(enrollmentId, offeringId));
    reload();
  };

  return { catalog: data, loading, error, register, drop };
}
