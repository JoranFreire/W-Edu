import { EmptyPanel, listCls } from '@/components/admin/users/dossier/DossierParts';
import { occurrenceKindLabels, occurrenceSeverityLabels } from '@/lib/academic/schoolLifeLabels';
import { formatIsoDate } from '@/lib/dates';
import type { UserDossier } from '@/types/userDossier';

/** Ocorrencias do aluno em todas as turmas, mais recentes primeiro. */
export default function OccurrencesTab({ occurrences }: { occurrences: NonNullable<UserDossier['occurrences']> }) {
  if (occurrences.total === 0) return <EmptyPanel>Nenhuma ocorrência registrada.</EmptyPanel>;
  return (
    <div className="space-y-2">
      {occurrences.total > occurrences.recent.length && (
        <p className="text-xs text-gray-500 dark:text-gray-400">Mostrando as {occurrences.recent.length} mais recentes de {occurrences.total}.</p>
      )}
      <ul className={listCls}>
        {occurrences.recent.map((occurrence) => (
          <li key={occurrence.id} className="px-4 py-3">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatIsoDate(occurrence.occurred_on)} · {occurrenceKindLabels[occurrence.kind]} · {occurrenceSeverityLabels[occurrence.severity]}
            </p>
            <p className="text-sm text-gray-900 dark:text-white">{occurrence.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
