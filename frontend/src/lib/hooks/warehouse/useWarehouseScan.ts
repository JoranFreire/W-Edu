'use client';

import { useState } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import type { MaterialRequest } from '@/types/warehouse';

type Step = { kind: 'scanning' } | { kind: 'checking' } | { kind: 'found'; request: MaterialRequest } | { kind: 'error'; message: string };

/** Le o QR da requisicao: confere quem pediu e o que leva; confirma a retirada ou abre a devolucao. */
export function useWarehouseScan(onChanged: () => void) {
  const [step, setStep] = useState<Step>({ kind: 'scanning' });
  const [code, setCode] = useState('');

  const check = async (scanned: string) => {
    setStep({ kind: 'checking' });
    try {
      const { data } = await api.post<MaterialRequest>(endpoints.warehouse.lookup, { code: scanned });
      setCode(scanned);
      setStep({ kind: 'found', request: data });
    } catch (err) {
      setStep({ kind: 'error', message: apiErrorMessage(err, 'QR não reconhecido.') });
    }
  };
  const pickup = async () => {
    const { data } = await api.post<MaterialRequest>(endpoints.warehouse.pickup, { code });
    setStep({ kind: 'found', request: data });
    onChanged();
  };
  const registerReturn = async (requestId: string, body: unknown) => {
    const { data } = await api.post<MaterialRequest>(endpoints.warehouse.action(requestId, 'returns'), body);
    setStep({ kind: 'found', request: data });
    onChanged();
  };
  const restart = () => setStep({ kind: 'scanning' });
  return { step, check, pickup, registerReturn, restart };
}
