'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Discount, DiscountInput, SettleInput, TuitionCharge } from '@/types/tuition';

interface EnrollmentFinance {
  discounts: Discount[];
  charges: TuitionCharge[];
}

/** Bolsas, descontos e extrato da matricula; baixa da parcela (administracao). */
export function useEnrollmentFinance(enrollmentId: number) {
  const request = useCallback(async (): Promise<EnrollmentFinance> => {
    const [discounts, charges] = await Promise.all([
      api.get<Discount[]>(endpoints.tuition.discounts(enrollmentId)),
      api.get<TuitionCharge[]>(endpoints.tuition.statement(enrollmentId)),
    ]);
    return { discounts: discounts.data, charges: charges.data };
  }, [enrollmentId]);
  const { data, error, reload } = useApiQuery(request);

  const addDiscount = async (input: DiscountInput) => {
    await api.post(endpoints.tuition.discounts(enrollmentId), input);
    reload();
  };
  const deactivateDiscount = async (discountId: number) => {
    await api.post(endpoints.tuition.deactivateDiscount(discountId));
    reload();
  };
  const settle = async (chargeId: number, input: SettleInput) => {
    await api.post(endpoints.tuition.settle(chargeId), input);
    reload();
  };

  return { finance: data, error, addDiscount, deactivateDiscount, settle };
}
