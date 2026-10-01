'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { BenefitVoucher } from '@/types/benefitVouchers';

/** Beneficios liberados ao aluno (QR de retirada) e o historico. */
export function useMyVouchers() {
  const request = useCallback(() => api.get<BenefitVoucher[]>(endpoints.social.myVouchers).then((response) => response.data), []);
  const { data = [], loading, error } = useApiQuery(request);
  return { vouchers: data, loading, error };
}
