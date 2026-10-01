'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { BenefitVoucher, VoucherBatchResult } from '@/types/benefitVouchers';

/** Para quem liberar: presentes/inscritos de um encontro, a turma toda ou um aluno. */
export type VoucherTarget = { kind: 'meeting'; meetingId: string } | { kind: 'offering' } | { kind: 'student'; studentId: string };

export interface VoucherDraft {
  target: VoucherTarget;
  itemId: string;
  quantity: number;
  validUntil: string | null;
}

/** Beneficios liberados em QR na turma: liberar (encontro, turma ou aluno) e cancelar o que nao foi retirado. */
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
  /** Quantos foram liberados (no lote, os que ja tinham o item ficam de fora). */
  const release = async ({ target, itemId, quantity, validUntil }: VoucherDraft): Promise<number> => {
    const payload = { item_id: itemId, quantity, valid_until: validUntil };
    let released = 1;
    if (target.kind === 'student') {
      await api.post(endpoints.social.vouchers, { ...payload, student_id: target.studentId, class_offering_id: offeringId });
    } else {
      const url = target.kind === 'meeting' ? endpoints.social.meetingVouchers(target.meetingId) : endpoints.social.offeringVouchers(offeringId);
      released = (await api.post<VoucherBatchResult>(url, payload)).data.released;
    }
    refresh();
    return released;
  };
  const cancel = async (voucherId: string) => {
    await api.post(endpoints.social.cancelVoucher(voucherId));
    refresh();
  };
  return { vouchers: data, error, release, cancel };
}
