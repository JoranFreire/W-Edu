'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ItemMovement } from '@/types/warehouse';

/** Extrato do material: entradas, retiradas, devolucoes e perdas. */
export function useItemHistory(itemId: string) {
  const request = useCallback(() => api.get<ItemMovement[]>(endpoints.warehouse.history(itemId)).then((response) => response.data), [itemId]);
  const { data, error } = useApiQuery(request);
  return { movements: data, error };
}
