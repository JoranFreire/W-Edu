import { EmptyPanel, listCls } from '@/components/admin/users/dossier/DossierParts';
import { requestStatusLabels } from '@/lib/academic/warehouseLabels';
import { formatIsoDate } from '@/lib/dates';
import type { DossierMaterialRequest } from '@/types/userDossier';

/** Requisicoes ao almoxarifado: o que foi pedido, aprovado, retirado e devolvido. */
export default function MaterialsTab({ requests }: { requests: DossierMaterialRequest[] }) {
  if (requests.length === 0) return <EmptyPanel>Nenhuma requisição de material.</EmptyPanel>;
  return (
    <ul className={listCls}>
      {requests.map((request) => (
        <li key={request.id} className="px-4 py-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="font-medium text-gray-900 dark:text-white">{request.purpose}</p>
            <span className="text-xs text-gray-500 dark:text-gray-400">{requestStatusLabels[request.status]}</span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Uso em {formatIsoDate(request.needed_on)}{request.offering_name ? ` · ${request.offering_name}` : ''}
            {request.return_due_on ? ` · devolver até ${formatIsoDate(request.return_due_on)}` : ''}
          </p>
          <ul className="mt-2 space-y-0.5 text-sm text-gray-700 dark:text-gray-300">
            {request.lines.map((line) => (
              <li key={line.item_name}>
                {line.item_name}: pediu {line.requested}
                {line.approved !== null ? `, aprovado ${line.approved}` : ''}, recebeu {line.delivered}
                {line.returned > 0 ? `, devolveu ${line.returned}` : ''} {line.unit}
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
}
