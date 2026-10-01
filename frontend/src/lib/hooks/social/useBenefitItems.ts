'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { BenefitItem, BenefitItemInput, StockEntryInput } from '@/types/socialPrograms';

/** Itens de beneficio com saldo em estoque; cadastro e entrada de estoque. */
export function useBenefitItems() {
  const request = useCallback(() => api.get<BenefitItem[]>(endpoints.social.items).then((response) => response.data), []);
  const { data = [], error, reload } = useApiQuery(request);
  const create = async (input: BenefitItemInput) => {
    await api.post(endpoints.social.items, input);
    reload();
  };
  const receive = async (itemId: string, input: StockEntryInput) => {
    await api.post(endpoints.social.stock(itemId), input);
    reload();
  };
  return { items: data, error, create, receive };
}
