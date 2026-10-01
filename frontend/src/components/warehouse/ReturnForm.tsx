'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { MaterialRequest } from '@/types/warehouse';

/** Devolucao dos permanentes: quantidade devolvida e perdida/avariada por linha, com observacao (fica no historico). */
export default function ReturnForm({ request, onReturn }: { request: MaterialRequest; onReturn: (body: unknown) => Promise<void> }) {
  const loaned = request.lines.filter((line) => line.outstanding > 0);
  const [values, setValues] = useState<Record<string, { returned: string; lost: string }>>(
    Object.fromEntries(loaned.map((line) => [line.id, { returned: String(line.outstanding), lost: '0' }])),
  );
  const [note, setNote] = useState('');
  const submit = async () => {
    try {
      await onReturn({
        lines: loaned.map((line) => ({ line_id: line.id, returned: Number(values[line.id].returned || 0), lost: Number(values[line.id].lost || 0) })),
        note: note.trim() || null,
      });
      toast.success('Devolução registrada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar a devolução.'));
    }
  };
  return (
    <div className="space-y-2 rounded-lg bg-gray-50 p-3 dark:bg-gray-900/40">
      {loaned.map((line) => (
        <div key={line.id} className="flex flex-wrap items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <span className="w-48">{line.item_name} ({line.outstanding} fora)</span>
          <input type="number" min={0} aria-label={`Devolvidos de ${line.item_name}`} value={values[line.id].returned}
            onChange={(e) => setValues({ ...values, [line.id]: { ...values[line.id], returned: e.target.value } })} className={`${inputCls} w-20`} />
          devolvido(s)
          <input type="number" min={0} aria-label={`Perdidos de ${line.item_name}`} value={values[line.id].lost}
            onChange={(e) => setValues({ ...values, [line.id]: { ...values[line.id], lost: e.target.value } })} className={`${inputCls} w-20`} />
          perdido(s)/avariado(s)
        </div>
      ))}
      <input aria-label={`Observação da devolução de ${request.purpose}`} placeholder="Observação (ex.: avaria, quem devolveu)" value={note}
        onChange={(e) => setNote(e.target.value)} className={inputCls} />
      <button onClick={submit} aria-label={`Registrar devolução de ${request.purpose}`} className={secondaryButtonCls}>Registrar devolução</button>
    </div>
  );
}
