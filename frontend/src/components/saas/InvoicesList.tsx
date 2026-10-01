import type { ReactNode } from 'react';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate } from '@/lib/dates';
import { invoiceStatusLabels } from '@/lib/platform/saasLabels';
import type { PlatformInvoice } from '@/types/saas';

export default function InvoicesList({ invoices, actions }: { invoices: PlatformInvoice[]; actions?: (invoice: PlatformInvoice) => ReactNode }) {
  if (invoices.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma fatura.</p>;
  return (
    <ul className="divide-y divide-gray-100 dark:divide-gray-700">
      {invoices.map((invoice) => (
        <li key={invoice.id} className="flex flex-wrap items-center justify-between gap-3 py-2 text-sm">
          <span className="text-gray-800 dark:text-gray-200">
            {formatIsoDate(invoice.period_start)} a {formatIsoDate(invoice.period_end)} · {invoice.plan_name} · {formatMoney(invoice.amount_cents)}
            <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">vence {formatIsoDate(invoice.due_on)} · {invoiceStatusLabels[invoice.status]}</span>
          </span>
          {actions?.(invoice)}
        </li>
      ))}
    </ul>
  );
}
