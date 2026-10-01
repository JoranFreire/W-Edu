'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { MaterialRequest } from '@/types/warehouse';

/** Aprovacao por linha (zero recusa a linha), prazo de devolucao dos permanentes e recusa com motivo. */
export default function ApprovalForm({ request, onApprove, onReject }: {
  request: MaterialRequest;
  onApprove: (body: unknown) => Promise<void>;
  onReject: (note: string) => Promise<void>;
}) {
  const [quantities, setQuantities] = useState<Record<number, string>>(
    Object.fromEntries(request.lines.map((line) => [line.id, String(line.quantity_requested)])),
  );
  const [due, setDue] = useState(request.needed_on);
  const [note, setNote] = useState('');
  const hasDurable = request.lines.some((line) => line.kind === 'durable');
  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Não foi possível concluir.'));
    }
  };
  const approve = () => run(() => onApprove({
    lines: request.lines.map((line) => ({ line_id: line.id, quantity: Number(quantities[line.id] || 0) })),
    return_due_on: hasDurable ? due : null, note: note || null,
  }), 'Requisição analisada.');
  return (
    <div className="space-y-2 rounded-lg bg-gray-50 p-3 dark:bg-gray-900/40">
      {request.lines.map((line) => (
        <label key={line.id} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="number" min={0} max={line.quantity_requested} aria-label={`Aprovar ${line.item_name}`} value={quantities[line.id]}
            onChange={(e) => setQuantities({ ...quantities, [line.id]: e.target.value })} className={`${inputCls} w-24`} />
          de {line.quantity_requested} {line.unit} · {line.item_name}
        </label>
      ))}
      <div className="flex flex-wrap items-center gap-2">
        {hasDurable && <input type="date" aria-label="Devolver até" value={due} onChange={(e) => setDue(e.target.value)} className={`${inputCls} w-44`} />}
        <input aria-label="Observação da análise" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Observação" className={`${inputCls} w-64`} />
        <button onClick={approve} aria-label={`Aprovar requisição ${request.purpose}`} className={primaryButtonCls}>Aprovar</button>
        <button onClick={() => (note ? run(() => onReject(note), 'Requisição recusada.') : toast.error('Informe o motivo na observação.'))}
          aria-label={`Recusar requisição ${request.purpose}`} className={secondaryButtonCls}>Recusar</button>
      </div>
    </div>
  );
}
