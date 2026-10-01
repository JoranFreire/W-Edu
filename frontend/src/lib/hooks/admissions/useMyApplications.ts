'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Application } from '@/types/admissions';

/** Inscricoes do candidato: comprovantes, desistencia e confirmacao da vaga. */
export function useMyApplications() {
  const request = useCallback(() => api.get<Application[]>(endpoints.admissions.mine).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const upload = async (applicationId: string, kind: string, file: File) => {
    const form = new FormData();
    form.append('kind', kind);
    form.append('file', file);
    await api.post(endpoints.admissions.myDocuments(applicationId), form);
    reload();
  };
  const act = async (applicationId: string, action: 'withdraw' | 'confirm' | 'decline') => {
    await api.post(endpoints.admissions.myAction(applicationId, action));
    reload();
  };

  return { applications: data, loading, error, upload, act };
}
