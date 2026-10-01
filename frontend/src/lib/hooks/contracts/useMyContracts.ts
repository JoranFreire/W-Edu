'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { contractFileName } from '@/lib/academic/contractLabels';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Contract } from '@/types/contracts';

/** Contratos do aluno e dos dependentes de quem e responsavel financeiro: aceite e download. */
export function useMyContracts() {
  const request = useCallback(() => api.get<Contract[]>(endpoints.contracts.mine).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const accept = async (contractId: number) => {
    await api.post(endpoints.contracts.accept(contractId));
    reload();
  };
  const download = async (contract: Contract) => {
    const { data: blob } = await api.get<Blob>(endpoints.contracts.myPdf(contract.id), { responseType: 'blob' });
    saveBlob(blob, contractFileName(contract));
  };

  return { contracts: data, loading, error, accept, download };
}
