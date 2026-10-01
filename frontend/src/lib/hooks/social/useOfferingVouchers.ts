'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { BenefitVoucher, MeetingVoucherResult } from '@/types/benefitVouchers';

export interface MeetingVoucherDraft {
  meetingId: string;
  itemId: string;
  quantity: number;
  validUntil: string | null;
}

/** Beneficios liberados em QR na turma: liberar no encontro e cancelar o que nao foi retirado. */
export function useOfferingVouchers(offeringId: string, onChange?: () => void) {
  const request = useCallback(
    () => api.get<BenefitVoucher[]>(endpoints.social.offeringVouchers(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data, error, reload } = useApiQuery(request);
  const refresh = () => {
    reload();
    onChange?.();
  };
  const release = async ({ meetingId, itemId, quantity, validUntil }: MeetingVoucherDraft) => {
    const { data: result } = await api.post<MeetingVoucherResult>(
      endpoints.social.meetingVouchers(meetingId), { item_id: itemId, quantity, valid_until: validUntil },
    );
    refresh();
    return result;
  };
  const cancel = async (voucherId: string) => {
    await api.post(endpoints.social.cancelVoucher(voucherId));
    refresh();
  };
  return { vouchers: data, error, release, cancel };
}
