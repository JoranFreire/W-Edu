'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { requestStatusLabels } from '@/lib/academic/warehouseLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useMaterialRequestsAdmin } from '@/lib/hooks/warehouse/useMaterialRequestsAdmin';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { RequestStatus } from '@/types/warehouse';
import ApprovalForm from './ApprovalForm';
import RequestCard from './RequestCard';
import ReturnForm from './ReturnForm';

/** Fila do almoxarifado: aprovar ou recusar, registrar retirada e devolucao. */
export default function RequestsPanel() {
  const [status, setStatus] = useState<RequestStatus | ''>('pending');
  const { requests, error, act } = useMaterialRequestsAdmin(status);
  useErrorToast(error, 'Erro ao carregar as requisições.');
  const deliver = async (id: number) => {
    try {
      await act(id, 'deliver');
      toast.success('Retirada registrada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar a retirada.'));
    }
  };
  return (
    <section className={`${sectionCls} space-y-4`}>
      <select aria-label="Situação das requisições" value={status} onChange={(e) => setStatus(e.target.value as RequestStatus | '')} className={`${inputCls} w-64`}>
        <option value="">Todas</option>
        {optionsOf(requestStatusLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      {requests.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma requisição.</p> : (
        <ul className="space-y-3">
          {requests.map((request) => (
            <RequestCard key={request.id} request={request} showRequester>
              {request.status === 'pending' && (
                <ApprovalForm request={request} onApprove={(body) => act(request.id, 'approve', body)} onReject={(note) => act(request.id, 'reject', { note })} />
              )}
              {request.status === 'approved' && (
                <button onClick={() => deliver(request.id)} aria-label={`Registrar retirada de ${request.purpose}`} className={primaryButtonCls}>Registrar retirada</button>
              )}
              {request.status === 'delivered' && <ReturnForm request={request} onReturn={(body) => act(request.id, 'returns', body)} />}
            </RequestCard>
          ))}
        </ul>
      )}
    </section>
  );
}
