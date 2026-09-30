'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { CreditTransfer, CreditTransferOrigin } from '@/types/secretariat';

export interface CreditTransferInput {
  subject_id: number;
  origin: CreditTransferOrigin;
  source_institution: string | null;
  source_subject: string;
  grade: number | null;
  hours: number | null;
}

/** Pedidos de aproveitamento de estudos da matricula. */
export function useCreditTransfers(enrollmentId: number) {
  const request = useCallback(
    () => api.get<CreditTransfer[]>(endpoints.secretariat.creditTransfers(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const requestTransfer = async (input: CreditTransferInput) => {
    await api.post(endpoints.secretariat.creditTransfers(enrollmentId), input);
    reload();
  };
  const decide = async (transferId: number, approved: boolean, note: string | null) => {
    await api.post(endpoints.secretariat.creditDecision(transferId), { approved, note });
    reload();
  };

  return { transfers: data, loading, error, requestTransfer, decide };
}
