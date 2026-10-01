'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Consumption, MaterialRequest, WarehouseItem } from '@/types/warehouse';

/** Estoque baixo, emprestimos em atraso e consumo no periodo. */
export function useWarehouseReports(start: string, end: string) {
  const request = useCallback(async () => {
    const [lowStock, overdue, consumption] = await Promise.all([
      api.get<WarehouseItem[]>(endpoints.warehouse.lowStock),
      api.get<MaterialRequest[]>(endpoints.warehouse.overdue),
      api.get<Consumption>(endpoints.warehouse.consumption, { params: { start, end } }),
    ]);
    return { lowStock: lowStock.data, overdue: overdue.data, consumption: consumption.data };
  }, [start, end]);
  const { data, error } = useApiQuery(request);
  return { reports: data, error };
}
