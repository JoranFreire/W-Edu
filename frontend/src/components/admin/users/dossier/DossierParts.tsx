import type { ReactNode } from 'react';

/** Mensagem de aba sem registros. */
export function EmptyPanel({ children }: { children: ReactNode }) {
  return <p className="rounded-lg border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500 dark:border-gray-600 dark:text-gray-400">{children}</p>;
}

/** Titulo de um bloco dentro de uma aba. */
export function PanelTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-3 text-sm font-semibold text-gray-900 dark:text-white">{children}</h2>;
}

/** Indicador numerico do resumo. */
export function Stat({ label, value, tone = 'default' }: { label: string; value: ReactNode; tone?: 'default' | 'danger' }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className={`mt-1 text-xl font-semibold ${tone === 'danger' ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>{value}</p>
    </div>
  );
}

/** Linha da ficha lateral (rotulo e valor). */
export function FactRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-gray-500 dark:text-gray-400">{label}</dt>
      <dd className="text-sm text-gray-900 dark:text-white">{value || '—'}</dd>
    </div>
  );
}

export const listCls = 'divide-y divide-gray-100 rounded-lg border border-gray-200 dark:divide-gray-700 dark:border-gray-700';
export const rowCls = 'flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-center sm:justify-between';
export const badgeCls = 'rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300';
