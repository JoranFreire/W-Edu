'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { contractFileName } from '@/lib/academic/contractLabels';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Contract } from '@/types/contracts';

/** Contratos da matricula (secretaria): emissao, download e cancelamento. */
export function useEnrollmentContracts(enrollmentId: number) {
  const request = useCallback(
    () => api.get<Contract[]>(endpoints.contracts.enrollment(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const issue = async (templateId: number, termId: number | null) => {
    await api.post(endpoints.contracts.enrollment(enrollmentId), { template_id: templateId, term_id: termId });
    reload();
  };
  const cancel = async (contractId: number) => {
    await api.post(endpoints.contracts.cancel(contractId));
    reload();
  };
  const download = async (contract: Contract) => {
    const { data: blob } = await api.get<Blob>(endpoints.contracts.pdf(contract.id), { responseType: 'blob' });
    saveBlob(blob, contractFileName(contract));
  };

  return { contracts: data, error, issue, cancel, download };
}
