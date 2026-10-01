import type { ReactNode } from 'react';
import { deliveryAudit, requestStatusCls, requestStatusLabels } from '@/lib/academic/warehouseLabels';
import { formatIsoDate } from '@/lib/dates';
import type { MaterialRequest } from '@/types/warehouse';

/** Requisicao: quem pediu, para quando, situacao e linhas (pedido, aprovado, entregue, devolvido). */
export default function RequestCard({ request, showRequester = false, children }: {
  request: MaterialRequest;
  showRequester?: boolean;
  children?: ReactNode;
}) {
  return (
    <li className="space-y-2 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
            {showRequester ? `${request.requester.name} · ` : ''}{request.purpose}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${requestStatusCls[request.status]}`}>{requestStatusLabels[request.status]}</span>
            {request.overdue && <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/20 dark:text-red-300">Devolução atrasada</span>}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Para {formatIsoDate(request.needed_on)}{request.class_offering_name ? ` · ${request.class_offering_name}` : ''}
            {request.return_due_on ? ` · devolver até ${formatIsoDate(request.return_due_on)}` : ''}
            {request.decision_note ? ` · ${request.decision_note}` : ''}
          </p>
        </div>
      </div>
      <ul className="text-sm text-gray-700 dark:text-gray-300">
        {request.lines.map((line) => (
          <li key={line.id}>
            {line.item_name}: {line.quantity_requested} {line.unit} pedido(s)
            {line.quantity_approved !== null ? ` · ${line.quantity_approved} aprovado(s)` : ''}
            {line.quantity_delivered ? ` · ${line.quantity_delivered} retirado(s)` : ''}
            {line.kind === 'durable' && line.quantity_delivered ? ` · ${line.quantity_returned} devolvido(s)${line.quantity_lost ? `, ${line.quantity_lost} perdido(s)` : ''}` : ''}
          </li>
        ))}
      </ul>
      {deliveryAudit(request) && <p className="text-xs text-gray-500 dark:text-gray-400">{deliveryAudit(request)}</p>}
      {children}
    </li>
  );
}
