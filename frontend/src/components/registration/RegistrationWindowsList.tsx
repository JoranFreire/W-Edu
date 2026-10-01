import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import StatusBadge from '@/components/common/StatusBadge';
import { dangerIconButtonCls, iconButtonCls } from '@/components/common/formStyles';
import { formatDateTime } from '@/lib/dates';
import type { RegistrationWindow } from '@/types/registration';

export default function RegistrationWindowsList({ windows, onEdit, onRemove }: {
  windows: RegistrationWindow[];
  onEdit: (window: RegistrationWindow) => void;
  onRemove: (window: RegistrationWindow) => void;
}) {
  if (windows.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma janela cadastrada.</p>;
  return (
    <ul className="divide-y divide-gray-100 dark:divide-gray-700">
      {windows.map((item) => (
        <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
          <div className="space-y-1">
            <p className="flex items-center gap-2 font-medium text-gray-900 dark:text-white">
              {item.name} <StatusBadge active={item.is_open} activeLabel="Aberta" inactiveLabel="Fechada" />
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {item.term_name} · {item.program_name ?? 'Todos os programas'} · {formatDateTime(item.opens_at)} a {formatDateTime(item.closes_at)}
              {item.max_credits !== null ? ` · até ${item.max_credits} créditos` : ''}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={() => onEdit(item)} aria-label={`Editar ${item.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
            <button onClick={() => onRemove(item)} aria-label={`Remover ${item.name}`} className={dangerIconButtonCls}><TrashIcon className="h-4 w-4" /></button>
          </div>
        </li>
      ))}
    </ul>
  );
}
