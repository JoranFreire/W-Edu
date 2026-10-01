'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { MaterialRequest, MaterialRequestInput } from '@/types/warehouse';

/** Requisicoes de material de quem pede: abrir, acompanhar e cancelar. */
export function useMyMaterialRequests() {
  const request = useCallback(() => api.get<MaterialRequest[]>(endpoints.warehouse.myRequests).then((response) => response.data), []);
  const { data = [], error, reload } = useApiQuery(request);
  const create = async (input: MaterialRequestInput) => {
    await api.post(endpoints.warehouse.requests, input);
    reload();
  };
  const cancel = async (requestId: number) => {
    await api.post(endpoints.warehouse.cancel(requestId));
    reload();
  };
  return { requests: data, error, create, cancel };
}
