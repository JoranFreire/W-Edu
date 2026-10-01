'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { BenefitVoucher } from '@/types/benefitVouchers';

/** Beneficios liberados do dependente: o responsavel mostra o QR na retirada. */
export function useDependentVouchers(studentId: string) {
  const request = useCallback(
    () => api.get<BenefitVoucher[]>(endpoints.guardians.vouchers(studentId)).then((response) => response.data),
    [studentId],
  );
  const { data = [], loading, error } = useApiQuery(request);
  return { vouchers: data, loading, error };
}
