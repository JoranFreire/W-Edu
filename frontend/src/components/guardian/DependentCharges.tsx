import { formatMoney } from '@/lib/academic/guardianLabels';
import type { DependentCharge } from '@/types/guardians';

const statusLabels: Record<string, string> = { pending: 'Em aberto', paid: 'Paga', overdue: 'Vencida', cancelled: 'Cancelada', refunded: 'Estornada' };

export default function DependentCharges({ charges }: { charges: DependentCharge[] }) {
  if (charges.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma cobrança.</p>;
  return (
    <ul className="divide-y divide-gray-200 dark:divide-gray-700">
      {charges.map((charge) => (
        <li key={charge.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
          <div>
            <p className="font-medium text-gray-900 dark:text-white">{formatMoney(charge.amount_cents, charge.currency)}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {statusLabels[charge.status] ?? charge.status}{charge.due_at ? ` · vence em ${new Date(charge.due_at).toLocaleDateString('pt-BR')}` : ''}
            </p>
          </div>
          {(charge.checkout_url || charge.bank_slip_url) && (
            <a href={charge.checkout_url ?? charge.bank_slip_url ?? '#'} target="_blank" rel="noreferrer" className="text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400">
              Pagar
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}
