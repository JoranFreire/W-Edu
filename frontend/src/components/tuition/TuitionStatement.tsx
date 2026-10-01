import type { ReactNode } from 'react';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate } from '@/lib/dates';
import { chargeStatusLabels } from '@/lib/finance/labels';
import type { TuitionCharge } from '@/types/tuition';

function composition(charge: TuitionCharge): string {
  const parts = [];
  if (charge.gross_amount_cents !== null && charge.discount_cents > 0) parts.push(`${formatMoney(charge.gross_amount_cents)} − ${formatMoney(charge.discount_cents)} de desconto`);
  if (charge.punctuality_discount_cents > 0) parts.push(`${formatMoney(charge.punctuality_discount_cents)} a menos até o vencimento`);
  return parts.join(' · ');
}

/** Extrato de mensalidades: valor, composicao, quanto pagar hoje (em aberto) ou quanto foi pago. */
export default function TuitionStatement({ charges, showStudent = false, actions }: {
  charges: TuitionCharge[];
  showStudent?: boolean;
  actions?: (charge: TuitionCharge) => ReactNode;
}) {
  if (charges.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma mensalidade.</p>;
  return (
    <ul className="divide-y divide-gray-100 dark:divide-gray-700">
      {charges.map((charge) => (
        <li key={charge.id} className="flex flex-wrap items-start justify-between gap-3 py-3">
          <div className="space-y-1">
            <p className="font-medium text-gray-900 dark:text-white">
              {showStudent && charge.student ? `${charge.student.name} · ` : ''}{charge.description ?? 'Cobrança'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {[charge.due_on ? `Vence em ${formatIsoDate(charge.due_on)}` : null, chargeStatusLabels[charge.status] ?? charge.status,
                charge.payer ? `Pagador: ${charge.payer.name}` : null].filter(Boolean).join(' · ')}
            </p>
            {composition(charge) && <p className="text-xs text-gray-500 dark:text-gray-400">{composition(charge)}</p>}
          </div>
          <div className="flex flex-col items-end gap-1 text-right">
            <p className="font-semibold text-gray-900 dark:text-white">{formatMoney(charge.amount_cents)}</p>
            {charge.quote && (
              <p className="text-xs text-gray-600 dark:text-gray-300">
                Hoje: {formatMoney(charge.quote.total_cents)}
                {charge.quote.fine_cents + charge.quote.interest_cents > 0 ? ` (multa ${formatMoney(charge.quote.fine_cents)} + juros ${formatMoney(charge.quote.interest_cents)})` : ''}
              </p>
            )}
            {charge.amount_paid_cents !== null && <p className="text-xs text-emerald-700 dark:text-emerald-300">Pago: {formatMoney(charge.amount_paid_cents)}</p>}
            {actions?.(charge)}
          </div>
        </li>
      ))}
    </ul>
  );
}
