'use client';

import { useState } from 'react';
import { QrCodeIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { requestStatusLabels } from '@/lib/academic/warehouseLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useMaterialRequestsAdmin } from '@/lib/hooks/warehouse/useMaterialRequestsAdmin';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { RequestStatus } from '@/types/warehouse';
import ApprovalForm from './ApprovalForm';
import ManualDeliveryForm from './ManualDeliveryForm';
import RequestCard from './RequestCard';
import ReturnForm from './ReturnForm';
import WarehouseScanPanel from './WarehouseScanPanel';

/** Fila do almoxarifado: aprovar ou recusar, retirada pelo QR do professor (ou sem ele, com motivo) e devolucao. */
export default function RequestsPanel() {
  const [status, setStatus] = useState<RequestStatus | ''>('pending');
  const { requests, error, act, reload } = useMaterialRequestsAdmin(status);
  const [scanning, setScanning] = useState(false);
  useErrorToast(error, 'Erro ao carregar as requisições.');
  const deliver = async (id: string, note: string) => {
    try {
      await act(id, 'deliver', { note });
      toast.success('Retirada registrada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar a retirada.'));
    }
  };
  return (
    <section className={`${sectionCls} space-y-4`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <select aria-label="Situação das requisições" value={status} onChange={(e) => setStatus(e.target.value as RequestStatus | '')} className={`${inputCls} w-64`}>
          <option value="">Todas</option>
          {optionsOf(requestStatusLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <button type="button" onClick={() => setScanning(!scanning)} className={primaryButtonCls}>
          <QrCodeIcon className="h-4 w-4" /> {scanning ? 'Fechar leitor' : 'Ler QR da requisição'}
        </button>
      </div>
      {scanning && <div className="rounded-lg border border-indigo-100 p-4 dark:border-indigo-900/40"><WarehouseScanPanel onChanged={reload} /></div>}
      {requests.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma requisição.</p> : (
        <ul className="space-y-3">
          {requests.map((request) => (
            <RequestCard key={request.id} request={request} showRequester>
              {request.status === 'pending' && (
                <ApprovalForm request={request} onApprove={(body) => act(request.id, 'approve', body)} onReject={(note) => act(request.id, 'reject', { note })} />
              )}
              {request.status === 'approved' && (
                <ManualDeliveryForm request={request} onDeliver={(note) => deliver(request.id, note)} />
              )}
              {request.status === 'delivered' && <ReturnForm request={request} onReturn={(body) => act(request.id, 'returns', body)} />}
            </RequestCard>
          ))}
        </ul>
      )}
    </section>
  );
}
