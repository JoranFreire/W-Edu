import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import { occurrenceKindLabels, occurrenceSeverityLabels } from '@/lib/academic/schoolLifeLabels';
import { formatIsoDate } from '@/lib/dates';
import type { UserDossier } from '@/types/userDossier';

/** Ocorrencias mais recentes do aluno (de todas as turmas). */
export default function OccurrencesSection({ occurrences }: { occurrences: NonNullable<UserDossier['occurrences']> }) {
  const title = occurrences.total > occurrences.recent.length ? `Ocorrências (${occurrences.recent.length} de ${occurrences.total})` : 'Ocorrências';
  return (
    <DossierSection title={title} icon={ExclamationTriangleIcon} isEmpty={occurrences.total === 0} emptyText="Nenhuma ocorrência registrada.">
      <ul className="space-y-2 text-sm">
        {occurrences.recent.map((occurrence) => (
          <li key={occurrence.id}>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatIsoDate(occurrence.occurred_on)} · {occurrenceKindLabels[occurrence.kind]} · {occurrenceSeverityLabels[occurrence.severity]}
            </p>
            <p className="text-gray-900 dark:text-white">{occurrence.description}</p>
          </li>
        ))}
      </ul>
    </DossierSection>
  );
}
