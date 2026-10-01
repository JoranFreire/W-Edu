'use client';

import { useState } from 'react';
import Spinner from '@/components/common/Spinner';
import { inputCls, sectionCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate, todayIso } from '@/lib/dates';
import { useWarehouseReports } from '@/lib/hooks/warehouse/useWarehouseReports';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { ConsumptionRow } from '@/types/warehouse';

function Rows({ title, rows }: { title: string; rows: ConsumptionRow[] }) {
  return (
    <div>
      <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">{title}</h3>
      {rows.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Sem consumo.</p> : (
        <ul className="text-sm text-gray-700 dark:text-gray-300">{rows.map((row) => <li key={row.label}>{row.label}: {row.quantity} · {formatMoney(row.cost_cents)}</li>)}</ul>
      )}
    </div>
  );
}

/** Estoque abaixo do minimo, devolucoes atrasadas e consumo por material, pessoa e turma. */
export default function ReportsPanel() {
  const [period, setPeriod] = useState({ start: `${todayIso().slice(0, 4)}-01-01`, end: todayIso() });
  const { reports, error } = useWarehouseReports(period.start, period.end);
  useErrorToast(error, 'Erro ao carregar os relatórios.');
  if (!reports) return <Spinner />;
  return (
    <section className={`${sectionCls} space-y-6`}>
      <div>
        <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">Estoque abaixo do mínimo</h3>
        {reports.lowStock.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum material.</p> : (
          <ul className="text-sm text-red-700 dark:text-red-300">{reports.lowStock.map((item) => <li key={item.id}>{item.name}: {item.available} de mínimo {item.min_stock}</li>)}</ul>
        )}
      </div>
      <div>
        <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">Devoluções atrasadas</h3>
        {reports.overdue.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma.</p> : (
          <ul className="text-sm text-gray-700 dark:text-gray-300">
            {reports.overdue.map((request) => (
              <li key={request.id}>{request.requester.name} · {request.purpose} · prazo {request.return_due_on ? formatIsoDate(request.return_due_on) : '—'}</li>
            ))}
          </ul>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-semibold text-gray-900 dark:text-white">Consumo de</span>
        <input type="date" aria-label="Início do período" value={period.start} onChange={(e) => setPeriod({ ...period, start: e.target.value })} className={`${inputCls} w-44`} />
        <span className="text-sm text-gray-600 dark:text-gray-300">a</span>
        <input type="date" aria-label="Fim do período" value={period.end} onChange={(e) => setPeriod({ ...period, end: e.target.value })} className={`${inputCls} w-44`} />
        <span className="text-sm text-gray-700 dark:text-gray-300">Total: {formatMoney(reports.consumption.total_cost_cents)}</span>
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Rows title="Por material" rows={reports.consumption.by_item} />
        <Rows title="Por pessoa" rows={reports.consumption.by_requester} />
        <Rows title="Por turma" rows={reports.consumption.by_offering} />
      </div>
    </section>
  );
}
