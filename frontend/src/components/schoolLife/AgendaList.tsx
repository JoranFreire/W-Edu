import { TrashIcon } from '@heroicons/react/24/outline';
import { dangerIconButtonCls } from '@/components/common/formStyles';
import { agendaKindLabels } from '@/lib/academic/schoolLifeLabels';
import { formatIsoDate } from '@/lib/dates';
import type { AgendaItem } from '@/types/schoolLife';

/** Itens da agenda por data; `showGroup` identifica a turma quando ha mais de uma. */
export default function AgendaList({ items, showGroup = false, onRemove }: {
  items: AgendaItem[];
  showGroup?: boolean;
  onRemove?: (item: AgendaItem) => void;
}) {
  if (items.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nada na agenda.</p>;
  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.id} className="flex items-start justify-between gap-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <div className="space-y-1">
            <p className="text-xs font-medium uppercase tracking-wide text-indigo-600 dark:text-indigo-300">
              {formatIsoDate(item.due_on)} · {agendaKindLabels[item.kind]}
            </p>
            <p className="font-medium text-gray-900 dark:text-white">{item.title}</p>
            {item.description && <p className="text-sm text-gray-600 dark:text-gray-300">{item.description}</p>}
            {(showGroup || item.class_offering_name) && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {[showGroup ? item.class_group_name : null, item.class_offering_name].filter(Boolean).join(' · ')}
              </p>
            )}
          </div>
          {onRemove && (
            <button onClick={() => onRemove(item)} aria-label={`Remover ${item.title}`} className={dangerIconButtonCls}>
              <TrashIcon className="h-4 w-4" />
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
