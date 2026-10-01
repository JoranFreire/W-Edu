'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { EntryInput, WarehouseItem, WarehouseItemInput } from '@/types/warehouse';

/** Materiais do almoxarifado com saldo; cadastro e entrada (operador). */
export function useWarehouseItems(onlyActive = false) {
  const request = useCallback(
    () => api.get<WarehouseItem[]>(endpoints.warehouse.items, { params: { only_active: onlyActive } }).then((response) => response.data),
    [onlyActive],
  );
  const { data = [], error, reload } = useApiQuery(request);
  const create = async (input: WarehouseItemInput) => {
    await api.post(endpoints.warehouse.items, input);
    reload();
  };
  const receive = async (itemId: number, input: EntryInput) => {
    await api.post(endpoints.warehouse.entries(itemId), input);
    reload();
  };
  return { items: data, error, reload, create, receive };
}
