import { CheckIcon, TrashIcon } from '@heroicons/react/24/outline';
import { dangerIconButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { occurrenceKindLabels, occurrenceSeverityLabels } from '@/lib/academic/schoolLifeLabels';
import { formatIsoDate } from '@/lib/dates';
import type { Occurrence } from '@/types/schoolLife';

const severityCls: Record<Occurrence['severity'], string> = {
  low: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  medium: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  high: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
};

/** Lista de ocorrencias; a acao de ciencia (responsavel) e a remocao (equipe) sao opcionais. */
export default function OccurrenceList({ occurrences, onAcknowledge, onRemove }: {
  occurrences: Occurrence[];
  onAcknowledge?: (occurrence: Occurrence) => void;
  onRemove?: (occurrence: Occurrence) => void;
}) {
  if (occurrences.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma ocorrência registrada.</p>;
  return (
    <ul className="space-y-3">
      {occurrences.map((occurrence) => {
        const label = `${occurrenceKindLabels[occurrence.kind]} de ${formatIsoDate(occurrence.occurred_on)}`;
        return (
          <li key={occurrence.id} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-1">
                <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
                  {label}
                  {occurrence.kind !== 'merit' && (
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityCls[occurrence.severity]}`}>
                      {occurrenceSeverityLabels[occurrence.severity]}
                    </span>
                  )}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">{occurrence.description}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {occurrence.reported_by ? `Registrada por ${occurrence.reported_by.name}` : 'Registrada pela escola'}
                  {occurrence.acknowledged_at && ` · Ciente em ${new Date(occurrence.acknowledged_at).toLocaleDateString('pt-BR')}`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {onAcknowledge && !occurrence.acknowledged_at && (
                  <button onClick={() => onAcknowledge(occurrence)} aria-label={`Ciente: ${label}`} className={secondaryButtonCls}>
                    <CheckIcon className="h-4 w-4" /> Ciente
                  </button>
                )}
                {onRemove && (
                  <button onClick={() => onRemove(occurrence)} aria-label={`Remover ${label}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
