'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { FundingReport } from '@/types/socialPrograms';

/** Prestacao de contas do financiador e download da planilha. */
export function useFundingReport(fundingId: string) {
  const request = useCallback(
    () => api.get<FundingReport>(endpoints.social.fundingReport(fundingId)).then((response) => response.data),
    [fundingId],
  );
  const { data, error } = useApiQuery(request);
  const downloadCsv = async () => {
    const { data: blob } = await api.get<Blob>(endpoints.social.fundingReportCsv(fundingId), { responseType: 'blob' });
    saveBlob(blob, `prestacao_contas_${fundingId}.csv`);
  };
  return { report: data, error, downloadCsv };
}
