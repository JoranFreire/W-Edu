'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import QrScanner from '@/components/common/QrScanner';
import Spinner from '@/components/common/Spinner';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useWarehouseScan } from '@/lib/hooks/warehouse/useWarehouseScan';
import RequestCard from './RequestCard';
import ReturnForm from './ReturnForm';

/** Balcao do almoxarifado: le o QR do professor para entregar o aprovado ou receber a devolucao. */
export default function WarehouseScanPanel({ onChanged }: { onChanged: () => void }) {
  const { step, check, pickup, registerReturn, restart } = useWarehouseScan(onChanged);
  const [typed, setTyped] = useState('');
  const confirmPickup = async () => {
    try {
      await pickup();
      toast.success('Retirada registrada com QR.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar a retirada.'));
    }
  };
  const submitTyped = (event: React.FormEvent) => {
    event.preventDefault();
    if (typed.trim()) check(typed.trim());
    setTyped('');
  };

  if (step.kind === 'checking') return <Spinner />;
  if (step.kind === 'error') {
    return (
      <div className="space-y-3">
        <p role="alert" className="text-sm font-medium text-red-600 dark:text-red-400">{step.message}</p>
        <button type="button" onClick={restart} className={secondaryButtonCls}>Ler outro QR</button>
      </div>
    );
  }
  if (step.kind === 'found') {
    const { request } = step;
    return (
      <div className="space-y-3">
        <ul><RequestCard request={request} showRequester /></ul>
        {request.status === 'approved' && <button type="button" onClick={confirmPickup} className={primaryButtonCls}>Confirmar retirada</button>}
        {request.status === 'delivered' && <ReturnForm request={request} onReturn={(body) => registerReturn(request.id, body)} />}
        {!['approved', 'delivered'].includes(request.status) && <p className="text-sm text-gray-500 dark:text-gray-400">Nada a entregar ou receber nesta requisição.</p>}
        <button type="button" onClick={restart} className={secondaryButtonCls}>Ler o próximo</button>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <QrScanner active onCode={check} />
      <form onSubmit={submitTyped} className="flex gap-2">
        <input aria-label="Código da requisição" placeholder="Ou digite o código" value={typed} onChange={(e) => setTyped(e.target.value)} className={inputCls} />
        <button className={secondaryButtonCls}>Conferir</button>
      </form>
    </div>
  );
}
