'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { MaterialRequest, RequestStatus } from '@/types/warehouse';

/** Requisicoes para o almoxarifado: aprovar (por linha), recusar, retirar e registrar devolucao. */
export function useMaterialRequestsAdmin(status: RequestStatus | '') {
  const request = useCallback(
    () => api.get<MaterialRequest[]>(endpoints.warehouse.requests, { params: { status: status || undefined } }).then((response) => response.data),
    [status],
  );
  const { data = [], error, reload } = useApiQuery(request);
  const act = async (id: string, action: 'approve' | 'reject' | 'deliver' | 'returns', body?: unknown) => {
    await api.post(endpoints.warehouse.action(id, action), body);
    reload();
  };
  return { requests: data, error, act };
}
