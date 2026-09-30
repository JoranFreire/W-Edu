'use client';

import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import type { ChargeActions } from '@/components/admin/finance/ChargesList';

/** Acoes sobre cobrancas; `onChanged` recarrega os dados apos cada acao. */
export function useChargeActions(onChanged: () => void): ChargeActions {
  const run = async (request: () => Promise<unknown>, success: string | null, failure: string) => {
    try {
      await request();
      onChanged();
      if (success) toast.success(success);
    } catch (error) {
      toast.error(apiErrorMessage(error, failure));
    }
  };

  return {
    sendToAsaas: (id) => run(() => api.post(endpoints.finance.chargeAsaas(id)), 'Cobrança enviada ao Asaas.', 'Erro ao enviar cobrança ao Asaas.'),
    markPaid: (id) => run(() => api.post(endpoints.finance.chargePaid(id)), null, 'Erro ao marcar como paga.'),
    markFailed: (id) => run(() => api.post(endpoints.finance.chargeFailed(id)), null, 'Erro ao marcar como falha.'),
  };
}
