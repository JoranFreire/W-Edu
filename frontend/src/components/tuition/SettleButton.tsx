'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { SettleInput, TuitionCharge } from '@/types/tuition';

/** Baixa da parcela na data do pagamento (calcula pontualidade ou multa e juros). */
export default function SettleButton({ charge, onSettle }: { charge: TuitionCharge; onSettle: (input: SettleInput) => Promise<void> }) {
  const [paidOn, setPaidOn] = useState(todayIso());
  const settle = async () => {
    try {
      await onSettle({ paid_on: paidOn, payment_method: 'manual' });
      toast.success('Pagamento registrado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar o pagamento.'));
    }
  };
  const label = charge.description ?? `cobrança ${charge.id}`;
  return (
    <div className="flex items-center gap-2">
      <input type="date" aria-label={`Data do pagamento de ${label}`} value={paidOn} onChange={(e) => setPaidOn(e.target.value)} className={`${inputCls} w-40`} />
      <button onClick={settle} aria-label={`Registrar pagamento de ${label}`} className={primaryButtonCls}>Baixar</button>
    </div>
  );
}
