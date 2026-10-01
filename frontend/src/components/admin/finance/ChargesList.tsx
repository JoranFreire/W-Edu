import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { chargeStatusLabels, formatCents } from '@/lib/finance/labels';
import type { Charge } from '@/types/finance';

const statusCls = (status: Charge['status']) =>
  status === 'paid'
    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
    : status === 'failed'
      ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300';

export interface ChargeActions {
  sendToAsaas: (id: string) => void;
  markPaid: (id: string) => void;
  markFailed: (id: string) => void;
}

export default function ChargesList({ charges, describe, actions }: {
  charges: Charge[];
  describe: (charge: Charge) => string;
  actions: ChargeActions | null;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {charges.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhuma cobrança cadastrada.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {charges.map((charge) => (
            <div key={charge.id} className="px-5 py-4 flex items-start justify-between gap-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{formatCents(charge.amount_cents)}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{charge.payment_method} • #{charge.id} • {describe(charge)}</p>
                {charge.description && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{charge.description}</p>}
                {(charge.checkout_url || charge.bank_slip_url || charge.pix_qr_code_payload) && (
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    {charge.checkout_url && <a href={charge.checkout_url} target="_blank" rel="noreferrer" className="font-medium text-indigo-600 dark:text-indigo-400">Checkout</a>}
                    {charge.bank_slip_url && <a href={charge.bank_slip_url} target="_blank" rel="noreferrer" className="font-medium text-indigo-600 dark:text-indigo-400">Boleto</a>}
                    {charge.pix_qr_code_payload && <button type="button" onClick={() => navigator.clipboard.writeText(charge.pix_qr_code_payload ?? '')} className="font-medium text-indigo-600 dark:text-indigo-400">Copiar Pix</button>}
                  </div>
                )}
                {charge.gateway_reference && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Gateway: {charge.gateway_name} • {charge.gateway_reference} • {charge.gateway_status ?? 'sem status'}</p>}
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusCls(charge.status)}`}>{chargeStatusLabels[charge.status]}</span>
                {actions && (
                  <>
                    {charge.gateway_name === 'asaas' && (
                      <button onClick={() => actions.sendToAsaas(charge.id)} title="Enviar ao Asaas" className="rounded-lg border border-gray-300 px-2 py-2 text-xs font-medium text-gray-700 dark:border-gray-600 dark:text-gray-300">
                        Asaas
                      </button>
                    )}
                    <button onClick={() => actions.markPaid(charge.id)} title="Marcar como paga" aria-label="Marcar como paga" className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 text-green-600"><CheckIcon className="w-4 h-4" /></button>
                    <button onClick={() => actions.markFailed(charge.id)} title="Marcar como falha" aria-label="Marcar como falha" className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 text-red-600"><XMarkIcon className="w-4 h-4" /></button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
